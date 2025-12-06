# Use official Python runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (LibreOffice, FFmpeg, Tesseract, build tools)
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
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend-python/requirements.txt .

# Install Python dependencies from file
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend-python/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
