# File Converter - Python Backend

A high-performance, privacy-first file converter backend built with Python and Flask.

## Features

- **Multiple Format Support**: Images (JPEG, PNG, WebP, GIF), Documents (CSV, Excel, Parquet), and more
- **Recipe System**: Every conversion generates a reproducible YAML recipe with checksums
- **Quality Gates**: Automatic integrity checks with SSIM for images, validation for data files
- **Batch Processing**: Convert multiple files efficiently
- **Statistical Analysis**: Extract insights from CSV/Excel files
- **Performance Optimized**: Built with Flask and efficient Python libraries

## Installation

### Requirements
- Python 3.9+
- FFmpeg (optional, for video/audio)

### Setup

```bash
# Navigate to backend directory
cd backend-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Start the Flask server
python app.py

# Server runs on http://localhost:5000
```

## API Endpoints

### File Conversion

**POST /api/convert**
- Convert any supported file format
- Returns conversion result with recipe

**POST /api/conversions/image**
- Convert image format with quality control
- Parameters: `format`, `quality`

**POST /api/conversions/document/excel-to-csv**
- Convert Excel to CSV

**POST /api/conversions/document/csv-to-excel**
- Convert CSV to Excel

**POST /api/conversions/document/csv-to-parquet**
- Convert CSV to Parquet format

### Image Operations

**POST /api/conversions/image-metadata**
- Extract image metadata (dimensions, format, size, etc.)

**POST /api/conversions/image-resize**
- Resize image with aspect ratio preservation

**POST /api/conversions/image-thumbnail**
- Create thumbnail

### Data Validation

**POST /api/conversions/csv-validate**
- Validate CSV structure
- Check for required columns
- Detect null values

### Information

**GET /api/conversions/supported-formats**
- List all supported file formats

**GET /api/health**
- Health check endpoint

**GET /api/formats**
- Get comprehensive format information

## Module Structure

```
backend-python/
├── core/
│   ├── recipe_manager.py        # Recipe creation and validation
│   ├── image_converter.py        # Image format conversions
│   ├── document_converter.py     # Document format conversions
│   ├── quality_gate.py           # Quality assurance checks
│   └── conversion_engine.py      # Main orchestrator
├── app.py                         # Flask server
├── requirements.txt               # Python dependencies
└── README.md
```

## Core Modules

### RecipeManager
Handles YAML recipe generation, validation, and storage. Every conversion is tracked with:
- Input/output file hashes (SHA-256)
- Conversion parameters
- Quality check results
- Timeline of conversion steps

### ImageConverter
Converts images between formats with quality optimization:
- JPEG, PNG, WebP, GIF, BMP, TIFF support
- SSIM quality scoring
- Batch conversion
- Thumbnail generation
- Metadata extraction

### DocumentConverter
Handles tabular data conversions:
- CSV ↔ Excel ↔ Parquet
- CSV validation and statistics
- Batch operations
- Row/column extraction
- Data merging

### QualityGate
Ensures conversion quality:
- SSIM scoring for images
- Data integrity checks for tabular files
- File size sanity checks
- Rollback on quality failure

### ConversionEngine
Orchestrates all conversions:
- Format detection
- Recipe generation
- Quality checks
- Error handling
- Batch operations

## Example Usage

### Python API
```python
from core.conversion_engine import ConversionEngine
import asyncio

async def convert_image():
    engine = ConversionEngine()
    result = await engine.convert(
        "input.jpg",
        "webp",
        {"parameters": {"quality": 85}}
    )
    print(result)

asyncio.run(convert_image())
```

### cURL
```bash
# Convert image
curl -F "file=@photo.jpg" \
     -F "outputFormat=webp" \
     -F "quality=80" \
     http://localhost:5000/api/conversions/image

# Convert CSV to Excel
curl -F "file=@data.csv" \
     http://localhost:5000/api/conversions/document/csv-to-excel

# Validate CSV
curl -F "file=@data.csv" \
     -F "requiredColumns=[\"name\",\"email\"]" \
     http://localhost:5000/api/conversions/csv-validate
```

## Performance

- **Images**: ~0.5-2s per image (depends on size/format)
- **CSV/Excel**: ~0.1-0.5s per file
- **Batch Processing**: 10+ files simultaneously

## Configuration

Set environment variables:
```bash
export PORT=5000              # API port
export OUTPUT_DIR="./output"  # Output directory
export UPLOAD_DIR="./uploads" # Temp upload directory
```

## Future Enhancements

- [ ] FFmpeg integration for video/audio
- [ ] OCR support for PDF
- [ ] Cloud storage integration (Google Drive, OneDrive)
- [ ] Advanced compression options
- [ ] Performance metrics dashboard
- [ ] Recipe marketplace backend

## License

MIT

## Contributing

Contributions welcome! Please follow PEP 8 style guide.
