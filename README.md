# File Converter - Next-Gen Public File Converter

**Transparent, reproducible, and privacy-first file conversion platform** — The GitHub of file conversions.

## 🎯 Vision

Transform file conversion from a black box into a transparent, auditable, and reproducible process. Users don't just convert files — they own the process, share recipes, and trust the results.

## 🌟 Key Features

### 1. **Recipe-Based Conversions**
- Every conversion produces a human-readable YAML recipe
- Includes checksums, parameters, quality metrics, and timeline
- Perfect for reproducibility and sharing workflows

### 2. **Quality Guarantees**
- Automatic integrity checks (SSIM for images, schema validation for data)
- Rollback on quality failure
- Transparent quality scoring

### 3. **Privacy-First**
- Local conversion option (offline)
- Optional cloud integration with user's own storage
- No hidden data processing

### 4. **High Performance**
- Python backend for optimized data processing
- Batch conversion support
- Efficient format-specific libraries

### 5. **Multiple Formats**
- **Images**: JPEG, PNG, WebP, GIF, BMP, TIFF
- **Documents**: CSV, Excel (XLSX), Parquet, PDF
- **Video/Audio**: MP4, WebM, MOV, AVI, MP3, WAV (with FFmpeg)

## 📦 Project Structure

```
File-Converter/
├── converter/                   # Original Node.js structure
│   ├── backend/                 # Express API
│   ├── frontend/                # React UI (planned)
│   ├── cli/                     # Command-line tool
│   ├── core/                    # Shared conversion logic
│   ├── tests/                   # Test suite
│   └── docs/                    # Documentation
│
├── backend-python/              # Python Flask backend
│   ├── core/                    # Core conversion engines
│   │   ├── recipe_manager.py    # Recipe generation
│   │   ├── image_converter.py   # Image conversions
│   │   ├── document_converter.py # Document conversions
│   │   ├── quality_gate.py      # Quality assurance
│   │   └── conversion_engine.py # Main orchestrator
│   ├── app.py                   # Flask server
│   └── requirements.txt         # Dependencies
│
├── plan.txt                     # Business plan
└── README.md                    # This file
```

## 🚀 Quick Start

### Python Backend (Recommended)

```bash
# Setup
cd backend-python
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run
python app.py
# Server at http://localhost:5000
```

### Node.js Backend (Alternative)

```bash
# Setup
cd converter
npm install

# Run
npm start
# Server at http://localhost:3000
```

## 📚 API Examples

### Convert Image
```bash
curl -F "file=@photo.jpg" \
     -F "format=webp" \
     -F "quality=80" \
     http://localhost:5000/api/conversions/image
```

### Convert CSV to Excel
```bash
curl -F "file=@data.csv" \
     http://localhost:5000/api/conversions/document/csv-to-excel
```

### Get Image Metadata
```bash
curl -F "file=@photo.jpg" \
     http://localhost:5000/api/conversions/image-metadata
```

### Validate CSV
```bash
curl -F "file=@data.csv" \
     -F "requiredColumns=[\"name\",\"email\"]" \
     http://localhost:5000/api/conversions/csv-validate
```

## 🔑 Core Concepts

### Recipe System
Every conversion generates a recipe with:
```yaml
version: '1.0'
metadata:
  created: '2025-12-05T14:30:22Z'
  userId: user@example.com
  description: Convert photo to WebP

input:
  file: vacation_photo.jpg
  format: jpg
  size: 3842957
  hash: 4a5b6c7d8e9f...

output:
  file: vacation_photo_1733404222000.webp
  format: webp
  parameters:
    quality: 80

quality:
  passed: true
  checks:
    - name: file_size
      score: valid
    - name: image_ssim
      score: 0.923  # 92.3% similarity

manifest:
  checksums:
    input: 4a5b6c7d...
    output: 5b6c7d8e...
  timeline: [...]
```

### Quality Gates
- **SSIM Scoring**: Measures image similarity (0-1 scale)
- **Data Validation**: Row/column count checks for tabular data
- **File Size Checks**: Prevents unexpectedly large/small outputs
- **Auto Rollback**: Fails and cleans up if quality is poor

### Reproducibility
```bash
# Re-run exact conversion from recipe
converter rerun -r vacation_photo.recipe.yaml

# Verify integrity
converter verify -r vacation_photo.recipe.yaml -i input.jpg -o output.webp
```

## 💡 Business Model

- **Free Tier**: Unlimited local conversions, basic recipes
- **Pro Plan**: Advanced OCR, batch jobs, cloud integrations, recipe marketplace
- **Enterprise**: Policy-driven conversions, audit logs, admin dashboards

## 🛣️ Roadmap

### Phase 1 (Month 1-2): ✅ In Progress
- [x] Core engine (docs, images, video presets)
- [x] Recipe/manifest system
- [x] Python backend with Flask
- [ ] Basic web UI

### Phase 2 (Month 3-4): Coming Next
- [ ] Pipelines & workflow builder
- [ ] Advanced quality gates with ML
- [ ] PDF OCR integration
- [ ] Cloud storage integration

### Phase 3 (Month 5)
- [ ] Public beta
- [ ] Transparency dashboard
- [ ] Performance benchmarks

### Phase 4 (Month 6)
- [ ] Recipe marketplace
- [ ] Community templates
- [ ] Public API with rate limiting

## 🎯 Why It's Different

| Feature | Us | Zamzar | CloudConvert |
|---------|----|----|-----|
| **Privacy First** | ✅ Local conversion | ❌ Server-based | ❌ Server-based |
| **Reproducible** | ✅ Recipes | ❌ No | ❌ No |
| **Quality Verified** | ✅ SSIM checks | ❌ No | ❌ Limited |
| **Transparent** | ✅ Full audit trail | ❌ Black box | ⚠️ Limited |
| **Open Source** | ✅ MIT | ❌ Closed | ❌ Closed |
| **Free Tier** | ✅ Unlimited local | ⚠️ 10 files/day | ⚠️ Limited |

## 📖 Documentation

- [Recipe System Guide](./converter/docs/RECIPES.md)
- [Python Backend README](./backend-python/README.md)
- [API Reference](./converter/docs/API.md) (coming soon)
- [Architecture Guide](./converter/docs/ARCHITECTURE.md) (coming soon)

## 🏗️ Architecture

### Python Backend (Current Focus)
- **Framework**: Flask + CORS
- **Image Processing**: Pillow, scikit-image
- **Data Processing**: Pandas, NumPy
- **Quality Metrics**: SSIM, custom validators
- **Performance**: ~0.5-2s per image, batch support

### Node.js Backend (Alternative)
- **Framework**: Express
- **Image Processing**: Sharp
- **Data Processing**: xlsx, csv-parser
- **CLI**: Full command-line interface

## 🔒 Security & Privacy

- Checksums verify file integrity
- No external service calls for local conversions
- Optional user ID (anonymous supported)
- YAML recipes contain only file metadata, not content
- Works completely offline with local mode

## 📊 Supported Formats

### Images (Python + Pillow)
✅ JPEG • ✅ PNG • ✅ WebP • ✅ GIF • ✅ BMP • ✅ TIFF

### Documents
✅ CSV • ✅ Excel (XLSX) • ✅ Parquet • ⏳ PDF

### Video/Audio (FFmpeg)
⏳ MP4 • ⏳ WebM • ⏳ MOV • ⏳ AVI • ⏳ MP3 • ⏳ WAV

## 🛠️ Development

### Prerequisites
- Python 3.9+ (for backend)
- Node.js 16+ (for CLI/frontend)
- FFmpeg (for video/audio)

### Install & Run

```bash
# Python backend
cd backend-python
pip install -r requirements.txt
python app.py

# Node.js backend
cd converter
npm install
npm start

# CLI
cd converter
npm install
node cli/converter.js convert -i input.jpg -f webp
```

### Running Tests

```bash
cd converter
npm test
```

## 📈 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Image conversion | 0.5-2s | Depends on size/format |
| CSV→Excel | 0.1-0.5s | Per file |
| Quality checks | 0.2-1s | Parallel processing |
| Batch (10 files) | 2-5s | Concurrent |

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 (Python) or ESLint (JavaScript)
4. Write tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 💬 Community

- **Issues**: Report bugs on GitHub
- **Discussions**: Share ideas and feedback
- **Recipes**: Share your conversion workflows

## 🎓 Educational Value

This project demonstrates:
- Building production-ready API servers
- Quality assurance for data processing
- Transparent audit trails
- Privacy-first architecture
- Recipe/template systems
- Reproducible workflows

Perfect for learners interested in:
- Backend development
- Data processing
- File format handling
- Quality assurance
- System design

## 📞 Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**Made with ❤️ to bring transparency and trust to file conversion.**

👉 **Next Steps**: Read [Python Backend README](./backend-python/README.md) to get started!
