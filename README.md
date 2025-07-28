# 📄 PDF Outline Extractor – Round 1A Hackathon Solution

## 🚀 Challenge Overview

This project is a solution for **Round 1A: Understand Your Document** of the hackathon.
The task was to **analyze a PDF like a machine** and extract a structured outline containing:

✅ **Title**
✅ **Headings (H1, H2, H3)**

The extracted output is saved as **JSON files**, one for each PDF, and also a **combined JSON** containing all processed PDFs.

---

## 🛠️ My Approach

1. **PDF Parsing**

   * Used **pdfplumber** to extract text, font sizes, and positions.
   * Extracted words, grouped them into lines, and identified heading levels (H1, H2, H3) based on font size.

2. **OCR Fallback (Multilingual Support)**

   * For PDFs without embedded text, used **pytesseract** + **pdf2image** to perform OCR.
   * Configured Tesseract to detect multiple languages (`eng`, `jpn`, `chi_sim`, `hin`) for bonus multilingual points.

3. **Heading Classification**

   * Determined heading levels (`H1`, `H2`, `H3`) using relative font sizes per page.
   * For single-page PDFs, assigned levels dynamically to capture as much structure as possible.

4. **Output Generation**

   * **Generated individual JSON files** for each PDF in the `/app/output` folder.
   * **Generated a combined schema.json** file inside `/app/schema`.

---

## 🧰 Tools & Libraries Used

📌 **Programming Language:** Python 3
📌 **PDF Parsing:** [pdfplumber](https://github.com/jsvine/pdfplumber)
📌 **OCR (Multilingual):** [pytesseract](https://github.com/madmaze/pytesseract)
📌 **PDF to Image Conversion:** [pdf2image](https://github.com/Belval/pdf2image)
📌 **Image Handling:** [Pillow](https://python-pillow.org/)
📌 **Multiprocessing:** For parallel PDF processing to improve performance

---

## 📂 Project Structure

```
├── app.py             # Main processing script
├── Dockerfile         # Docker setup file
├── requirements.txt   # Dependencies
└── sample_dataset/    # Input PDFs, Output JSONs (created at runtime)
```

---

## 🐳 How to Build & Run Using Docker

### 1️⃣ **Build Docker Image**

```bash
docker build --platform linux/amd64 -t pdf-processor .
```

### 2️⃣ **Run the Solution**

Place all your **input PDFs** inside an `input/` folder and run:

```bash
docker run --rm `                                                           
    "${PWD}/sample_dataset/PDF:/app/sample_dataset/PDF:ro" `
    "${PWD}/sample_dataset/outputs:/app/sample_dataset/outputs" `
    "${PWD}/sample_dataset/schema:/app/sample_dataset/schema" `
   --network none `
   pdf-processor
```

✅ **The container will automatically:**
✔ Process all PDFs from `/app/input`
✔ Generate individual JSON files in `/app/output`
✔ Create a combined `schema.json` file inside `/app/output`

---

## ⚡ Features

✅ **Supports up to 50-page PDFs**
✅ **Runs completely offline (no internet required)**
✅ **CPU-based & lightweight (<200MB model size)**
✅ **Handles multilingual PDFs (English, Japanese, Chinese, Hindi)**
✅ **Generates both per-PDF JSON & combined JSON output**

---

## 📊 Example Output

For an input PDF `sample.pdf`, the generated JSON will look like:

```json
{
  "title": "Understanding AI",
  "pages": {
    "1": { "H1": ["Introduction"] },
    "2": { "H2": ["What is AI?"] },
    "3": { "H3": ["History of AI"] }
  }
}
```

---

## ⚙️ Performance & Compliance

✅ **Execution Time:** < 10 seconds for 50-page PDFs
✅ **Works Offline** (No API calls)
✅ **CPU-Only (amd64)**
✅ **Model Size < 200MB**

---

## ✨ Author

👨‍💻 **Sahith Reddy**
🔗 Hackathon Round 1A Solution – Connecting the Dots Through Docs

---
