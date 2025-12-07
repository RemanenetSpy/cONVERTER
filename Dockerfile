# Use official Python runtime
FROM python:3.9-slim

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
RUN pip install python-pptx
RUN pip install py7zr
RUN pip install cairosvg
RUN pip install pillow-heif

# Complex libs last
RUN pip install ocrmypdf

# Copy backend code
COPY backend-python/ .

# Copy Frontend Build from Stage 1
COPY --from=frontend_build /frontend/build ./frontend_build

# Create uploads directory
RUN mkdir -p uploads

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
