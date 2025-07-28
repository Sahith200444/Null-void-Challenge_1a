import pdfplumber
import json
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Any
import time
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
# Configuration
INPUT_DIR = Path("/app/sample_dataset/PDF")
OUTPUT_DIR = Path("/app/sample_dataset/outputs")
OUTPUT_SCHEMA = Path("/app/sample_dataset/schema")
MAX_PAGES = 50
FONT_LEVELS = 3  # H1..H3

def extract_text_with_ocr(pdf_path: Path) -> list:
    """Extract text from PDF using OCR (supports multiple languages)."""
    from pytesseract import image_to_string
    from pdf2image import convert_from_path

    all_lines = []
    try:
        images = convert_from_path(pdf_path, dpi=300)
        for page_num, img in enumerate(images, start=1):
            # Detect multiple languages (English, Japanese, Chinese, Hindi)
            text = image_to_string(img, lang="eng+jpn+chi_sim+hin")

            for line in text.split("\n"):
                if line.strip():
                    all_lines.append({
                        "text": line.strip(),
                        "size": 0,
                        "page": page_num,
                        "y0": 0
                    })
    except Exception as e:
        print(f"OCR failed for {pdf_path}: {e}")

    return all_lines


def extract_lines(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extract lines with font information from PDF."""
    all_lines = []
    header_footer_margin = 0.08 

    try:
        with pdfplumber.open(pdf_path) as pdf:

            is_single_page = len(pdf.pages) == 1
            
            for pno, page in enumerate(pdf.pages, start=1):
                if pno > MAX_PAGES:
                    break
                    
                height = page.height
                words = page.extract_words(
                    keep_blank_chars=True,
                    x_tolerance=3,
                    y_tolerance=3,
                    extra_attrs=["size", "fontname", "top", "bottom"]
                )
                                # If no words found on the first page → use OCR
                if not words and pno == 1:
                    print(f"No embedded text found, using OCR for {pdf_path}")
                    return extract_text_with_ocr(pdf_path)

                header_boundary = height * header_footer_margin
                footer_boundary = height * (1 - header_footer_margin)
                
                lines_dict = {}
                for word in words:
                    y_pos = round(word['top'], 1)
                    
                  
                    if not is_single_page and pno > 1:
                        if y_pos < header_boundary or y_pos > footer_boundary:
                            continue
                    
                    lines_dict.setdefault(y_pos, []).append(word)
                
                
                for y_pos, line_words in lines_dict.items():
                    line_words.sort(key=lambda w: w['x0'])
                    text = " ".join(w['text'] for w in line_words).strip()
                    
                    if not text:
                        continue
                    
                    if is_single_page:
                        if text.replace('.', '').isdigit():
                            continue
                    else:
                        
                        if text.replace('.', '').isdigit() or len(text) < 3:
                            continue
                        if any(skip in text.lower() for skip in ['version', 'page', 'of']):
                            continue
                    
                    size = round(max(w.get('size', 0) for w in line_words), 1)
                    all_lines.append({
                        "text": text,
                        "size": size,
                        "page": pno,
                        "y0": y_pos
                    })
                    
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return []
    
    return all_lines

def organize_headings_by_page(lines: List[Dict[str, Any]]) -> Dict[int, Dict[str, List[str]]]:
    """Organize headings by page number with H1, H2, H3 hierarchy."""
    by_page = {}
    
    
    is_single_page = len(set(line["page"] for line in lines)) == 1
    
    
    page_lines = {}
    for line in lines:
        page = line["page"]
        if page not in page_lines:
            page_lines[page] = []
        page_lines[page].append(line)
    
    for page, lines in page_lines.items():
       
        sizes = sorted({l["size"] for l in lines}, reverse=True)
        if is_single_page:
            # For single page, use all unique sizes
            sizes = sizes[:len(sizes)]
        else:
            # For multi-page, use top 3 sizes
            sizes = sizes[:3]
            
        if not sizes:
            continue
            
        page_headings = {"H1": [], "H2": [], "H3": []}
        current_h2 = []
        
        # Sort lines by vertical position
        lines.sort(key=lambda x: x["y0"])
        
        for line in lines:
            size = line["size"]
            text = line["text"].strip()
            
            if not text:
                continue
                
            # For single page, include everything except page numbers
            if is_single_page:
                if text.replace('.', '').isdigit():
                    continue
                # Assign to closest heading level
                idx = sizes.index(size) if size in sizes else len(sizes) - 1
                level = f"H{min(idx + 1, 3)}"
                if text not in page_headings[level]:
                    page_headings[level].append(text)
            else:
                # Multi-page logic remains the same
                if size == sizes[0]:
                    if text not in page_headings["H1"]:
                        page_headings["H1"].append(text)
                elif size == sizes[1]:
                    current_h2.append(text)
                elif size == sizes[2] and text:
                    if text not in page_headings["H3"]:
                        page_headings["H3"].append(text)
        
        # Join H2 content if needed
        if not is_single_page and current_h2:
            h2_text = " ".join(current_h2)
            h2_text = " ".join(h2_text.split())
            page_headings["H2"] = [h2_text]
        
        # Only include non-empty heading levels
        clean_headings = {k: v for k, v in page_headings.items() if v}
        if clean_headings:
            by_page[page] = clean_headings
            
    return by_page

def process_pdf(pdf_path: Path) -> Dict[str, Any]:
    """Process a single PDF file."""
    try:
        lines = extract_lines(pdf_path)
        if not lines:
            return {
                "title": pdf_path.stem,
                "pages": {}
            }

        # Get title from largest font size on first page
        first_page = [l for l in lines if l["page"] == 1]
        if first_page:
            max_size = max(l["size"] for l in first_page)
            title = next((l["text"] for l in first_page 
                         if l["size"] == max_size), pdf_path.stem)
        else:
            title = pdf_path.stem

        # Organize headings by page
        pages = organize_headings_by_page(lines)

        return {
            "title": title,
            "pages": pages
        }
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return {
            "title": pdf_path.stem,
            "pages": {}
        }

def main():
    """Main processing function."""
    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}")
        return
        
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {INPUT_DIR}")
        return

    workers = min(len(pdfs), cpu_count())
    with Pool(workers) as pool:
        results = pool.map(process_pdf, pdfs)

        # Save individual JSON files for each PDF
    for pdf_path, pdf_result in zip(pdfs, results):
        individual_file = OUTPUT_DIR / f"{pdf_path.stem}.json"
        with open(individual_file, "w", encoding="utf-8") as f:
            json.dump(pdf_result, f, ensure_ascii=False, indent=2)

    # Save combined JSON for all PDFs
    output_path = OUTPUT_SCHEMA / "schema.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()