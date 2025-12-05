# Quick Start Guide

Get the File Converter running in 5 minutes!

## 🚀 Start the Python Backend

```bash
# 1. Navigate to backend directory
cd backend-python

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the server
python app.py
```

**Server will be running at:** http://localhost:5000

## 📄 Supported Conversions

### Images
- JPEG ↔ PNG ↔ WebP ↔ GIF ↔ BMP ↔ TIFF
- Quality control with SSIM scoring
- Batch processing
- Thumbnail generation
- Metadata extraction

### Documents  
- Excel ↔ CSV ↔ Parquet
- Data validation
- Statistics generation
- Batch operations

## 🧪 Test Your Installation

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Convert an Image
```bash
# Save this image first, or use your own
curl -F "file=@yourimage.jpg" \
     -F "format=webp" \
     -F "quality=80" \
     http://localhost:5000/api/conversions/image
```

### 3. Convert CSV to Excel
```bash
curl -F "file=@data.csv" \
     http://localhost:5000/api/conversions/document/csv-to-excel
```

### 4. Get Supported Formats
```bash
curl http://localhost:5000/api/conversions/supported-formats
```

## 📁 Generated Files

After conversion, files are saved to:
- **Output files**: `backend-python/output/`
- **Upload temp**: `backend-python/uploads/`
- **Recipes**: `backend-python/output/*.recipe.yaml`

## 🔑 Key Features to Try

### Recipe System
Every conversion creates a YAML recipe showing:
- Input/output file checksums
- Conversion parameters
- Quality scores
- Complete timeline

Example recipe location:
```
backend-python/output/yourimage_1733404222000.recipe.yaml
```

### Quality Checks
- **Image SSIM Score**: Measures visual similarity (0-1)
- **File Size Check**: Ensures reasonable compression
- **Data Integrity**: Validates CSV/Excel structure

## 📝 Python Requirements

Key libraries installed:
- **Flask**: Web framework
- **Pillow**: Image processing
- **Pandas**: Data processing
- **NumPy**: Numerical computing
- **scikit-image**: Image quality metrics
- **PyYAML**: Recipe generation

## 🎯 Next Steps

1. **Try image conversions** - Test with JPEG, PNG, WebP
2. **Test document conversions** - Excel ↔ CSV ↔ Parquet
3. **Check recipes** - Open .recipe.yaml files
4. **Verify quality** - Check SSIM scores and checksums
5. **Batch processing** - Convert multiple files

## ⚙️ Configuration

Set environment variables:
```bash
export PORT=5000              # Change API port
export OUTPUT_DIR="./output"  # Output directory
```

## 🆘 Troubleshooting

**Port already in use:**
```bash
export PORT=5001
python app.py
```

**Module import errors:**
```bash
pip install -r requirements.txt --upgrade
```

**File too large:**
- Default limit is 500MB
- Edit `app.py` to change

## 📚 API Documentation

Full API details in [Python Backend README](../backend-python/README.md)

## 💡 Tips

- Check `backend-python/output/` for results
- View `.recipe.yaml` files to understand conversions
- Try quality parameters: `quality=85` for better results
- Use batch endpoints for multiple files
- Check logs for any conversion issues

## 🎓 What You're Learning

This project teaches:
- Building REST APIs with Flask
- Image processing with Pillow
- Data transformation with Pandas
- Quality assurance automation
- Recipe/template systems
- Audit trail creation

---

**Happy Converting!** 🎉

Questions? Check the [main README](../README.md) or [Python Backend README](../backend-python/README.md)
