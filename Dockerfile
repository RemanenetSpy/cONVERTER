# Use official Python runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (LibreOffice, FFmpeg, Tesseract OCR)
RUN apt-get update && apt-get install -y \
    libreoffice \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    default-jre \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first (for caching)
COPY backend-python/requirements.txt .

# Install Python dependencies (including our new High Quality libs)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir xhtml2pdf pdfplumber pdf2docx python-docx reportlab pandas openpyxl pillow pydub flask flask-cors werkzeug

# Copy backend code
COPY backend-python/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
