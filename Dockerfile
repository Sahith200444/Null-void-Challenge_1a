FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app.py .

# Create directories with correct permissions
RUN mkdir -p /app/input /app/output && \
    chown -R 1000:1000 /app/output && \
    chmod 755 /app/input && \
    chmod 777 /app/output

# Run as non-root user
USER 1000:1000

# Command to run the application
CMD ["python", "app.py"]
