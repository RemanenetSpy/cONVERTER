# Use official Python runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Split into multiple RUNs is cleaner for debugging, but single RUN is better for layer size.
# Fixed: libgl1-mesa-glx -> libgl1 (Debian 12+ compat)
# Optimized: libreoffice -> libreoffice-writer libreoffice-calc
RUN apt-get update && apt-get install -y \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-java-common \
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
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    python3-dev \
    build-essential \
    libfreetype6-dev \
    gcc \
    g++ \
    make \
    qpdf \
    pkg-config \
    unpaper \
    libgl1 \
    libglib2.0-0 \
    libcairo2-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend-python/requirements.txt .

# Upgrade pip and build tools
RUN pip install --upgrade pip setuptools wheel

# Install dependencies sequentially to debug failures and avoid OOM
RUN pip install Flask Flask-Cors Werkzeug gunicorn Flask-Limiter
RUN pip install pandas openpyxl psutil
RUN pip install Pillow
RUN pip install reportlab
RUN pip install xhtml2pdf
RUN pip install pdfplumber
RUN pip install opencv-python-headless
RUN pip install pydub
RUN pip install python-docx
RUN pip install pdf2docx
RUN pip install scikit-image
RUN pip install PyPDF2

# Complex libs last
RUN pip install ocrmypdf

# Copy backend code
COPY backend-python/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
