# 🚀 Complete Setup Guide - Frontend + Backend

## 📋 Table of Contents
1. [Backend Setup (Python Flask)](#backend-setup)
2. [Frontend Setup (React)](#frontend-setup)
3. [Running Both Services](#running-both-services)
4. [Usage Examples](#usage-examples)
5. [Troubleshooting](#troubleshooting)

---

## Backend Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Navigate to Backend
```bash
cd backend-python
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Backend Server
```bash
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Backend Features Available:
- ✅ Image conversions (JPG, PNG, WebP, GIF, BMP, TIFF)
- ✅ Document conversions (CSV, Excel, Parquet)
- ✅ Quality assurance with SSIM scoring
- ✅ Complete recipe/audit trail
- ✅ 19+ REST API endpoints

---

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm (comes with Node.js)

### Step 1: Navigate to Frontend
```bash
cd converter/frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

This will install:
- React 18.2.0
- Axios for API calls
- React Dropzone for file uploads
- Lucide React for icons
- And more...

### Step 3: Configure Environment (Optional)
```bash
# Copy example env file
cp .env.example .env

# Edit if backend is on different address
# Default: http://localhost:5000/api
```

### Step 4: Start Frontend Development Server
```bash
npm start
```

**Expected Output:**
```
webpack compiled with X warnings
You can now view file-converter-ui in the browser.

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

---

## Running Both Services

### Terminal 1: Backend
```bash
cd backend-python
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

### Terminal 2: Frontend
```bash
cd converter/frontend
npm start
```

### Open Browser
Navigate to: **http://localhost:3000**

You should see:
- ✨ Beautiful gradient header
- 📁 File upload dropzone
- ⚙️ Conversion panel
- 📜 Conversion history (empty initially)
- 🟢 Backend Connected indicator (top right)

---

## Usage Examples

### Example 1: Convert JPG to WebP

1. **Upload Phase:**
   - Drag a `.jpg` file into the dropzone
   - OR click to browse and select file
   - File appears with details

2. **Convert Phase:**
   - See "WebP" button in output formats
   - Adjust quality slider (0-100%)
   - Click "Convert Now"

3. **Download Phase:**
   - See success message
   - Conversion appears in history
   - Click "Download" to save file

### Example 2: Convert CSV to Excel

1. **Upload Phase:**
   - Select a `.csv` file
   - Frontend shows Excel as option

2. **Convert Phase:**
   - Click "Excel" format
   - Click "Convert Now"

3. **Results:**
   - Download `.xlsx` file
   - Quality metrics show row/column preservation

### Example 3: View Recipe (Audit Trail)

1. After successful conversion
2. Click "View Recipe" in history
3. See complete conversion record:
   - Input file hash (SHA-256)
   - Output file hash
   - Quality checks performed
   - Timestamp and parameters
   - Timeline of events

---

## 🎯 Frontend Features

### File Uploader
- Drag & drop support
- 500MB file limit
- Shows file type and size
- Supported formats list

### Conversion Panel
- Smart format suggestions
- Quality slider for images
- Advanced options:
  - Preserve metadata
  - Keep original colors
  - Enable compression
- Real-time status

### History Panel
- Lists all conversions
- Shows timestamps
- Quality metrics
- Download converted files
- View complete recipes
- Remove items

### Health Check
- Fixed indicator (top right)
- Shows backend status:
  - 🟢 Connected
  - 🔴 Disconnected
  - 🟡 Checking
- Auto-refreshes every 30s

---

## 📊 API Endpoints Reference

### Health & Info
```bash
GET /api/health
GET /api/formats
```

### Image Conversions
```bash
POST /api/conversions/image
POST /api/conversions/image-metadata
POST /api/conversions/image-resize
POST /api/conversions/image-thumbnail
```

### Document Conversions
```bash
POST /api/conversions/document/excel-to-csv
POST /api/conversions/document/csv-to-excel
POST /api/conversions/document/csv-to-parquet
POST /api/conversions/csv-validate
```

### Generic Conversion
```bash
POST /api/convert
```

### Example cURL Request
```bash
curl -X POST http://localhost:5000/api/conversions/image \
  -F "file=@input.jpg" \
  -F "output_format=webp" \
  -F "quality=85"
```

---

## 🔧 Configuration

### Backend Configuration
Edit `backend-python/app.py`:
```python
# File upload limit
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# CORS settings
CORS(app, origins=['http://localhost:3000'])

# Quality thresholds
image_quality_threshold = 0.8
csv_row_variance = 0.05
```

### Frontend Configuration
Edit `converter/frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_DEBUG=true
```

---

## 🐛 Troubleshooting

### Issue: "Backend Disconnected"
```
❌ Problem: Health check shows disconnected
✅ Solution:
   1. Ensure backend is running: python app.py
   2. Check port 5000 is not in use
   3. Verify backend console shows "Running on http://127.0.0.1:5000"
   4. Check REACT_APP_API_URL in .env
```

### Issue: "Cannot find module" on npm start
```
❌ Problem: npm start fails with module errors
✅ Solution:
   1. Delete node_modules: rm -rf node_modules
   2. Clear npm cache: npm cache clean --force
   3. Reinstall: npm install
   4. Try again: npm start
```

### Issue: "File upload failed"
```
❌ Problem: Upload fails after selecting file
✅ Solution:
   1. Check file size < 500MB
   2. Verify backend is running
   3. Check browser console (F12) for detailed error
   4. Try different file type
```

### Issue: "Port 3000 already in use"
```
❌ Problem: npm start says port 3000 in use
✅ Solution (Windows):
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F

✅ Solution (macOS/Linux):
   lsof -i :3000
   kill -9 <PID>
```

### Issue: "Port 5000 already in use"
```
❌ Problem: python app.py says port 5000 in use
✅ Solution (Windows):
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F

✅ Solution (macOS/Linux):
   lsof -i :5000
   kill -9 <PID>
```

### Issue: CORS Error in Browser Console
```
❌ Problem: "Cross-Origin Request Blocked"
✅ Solution:
   - Backend already has CORS enabled
   - Verify REACT_APP_API_URL is correct
   - Check backend console for errors
   - Restart both frontend and backend
```

---

## 📦 Project Structure

```
Converter/
├── backend-python/               # Python Flask Backend
│   ├── app.py                   # Main Flask server
│   ├── requirements.txt          # Python dependencies
│   └── core/
│       ├── conversion_engine.py  # Main orchestrator
│       ├── image_converter.py    # Image conversions
│       ├── document_converter.py # CSV/Excel/Parquet
│       ├── quality_gate.py       # Quality assurance
│       └── recipe_manager.py     # Audit trail generation
│
├── converter/
│   ├── frontend/                 # React Frontend (NEW!)
│   │   ├── package.json         # Dependencies
│   │   ├── public/
│   │   │   └── index.html       # HTML template
│   │   └── src/
│   │       ├── App.jsx          # Main app
│   │       ├── index.js         # Entry point
│   │       └── components/
│   │           ├── FileUploader.jsx
│   │           ├── ConversionPanel.jsx
│   │           ├── HistoryPanel.jsx
│   │           └── HealthCheck.jsx
│   │
│   ├── backend/                  # Node.js Backend (Alternative)
│   ├── core/                     # Shared logic
│   ├── tests/                    # Test suite
│   └── docs/                     # Documentation
│
├── README.md                      # Main documentation
└── QUICKSTART.md                 # Quick start guide
```

---

## ✨ Features Summary

### ✅ Image Processing
- Convert between 6+ formats (JPG, PNG, WebP, GIF, BMP, TIFF)
- Quality slider (0-100%)
- SSIM quality scoring
- Metadata extraction
- Resize, thumbnail generation

### ✅ Document Processing
- CSV ↔ Excel conversions
- CSV → Parquet conversion
- Data validation
- Statistics calculation
- Row/column preservation

### ✅ Quality Assurance
- Automatic integrity checks
- SSIM-based image quality scoring
- Data consistency validation
- File size sanity checks
- Automatic rollback on failure

### ✅ Transparency
- Complete recipe/audit trail
- SHA-256 checksums for all files
- Timeline of all operations
- Quality metrics recorded
- Reproducible conversions

### ✅ User Experience
- Beautiful gradient UI
- Drag & drop file upload
- Real-time health checks
- Download converted files
- Conversion history
- Advanced options available

---

## 🚀 Next Steps

1. **Start Backend:**
   ```bash
   cd backend-python
   python app.py
   ```

2. **Start Frontend:**
   ```bash
   cd converter/frontend
   npm start
   ```

3. **Open Browser:**
   Navigate to http://localhost:3000

4. **Try Converting:**
   - Upload a file
   - Select output format
   - Click convert!

---

## 📞 Support

- **Backend Issues:** Check `backend-python/` logs
- **Frontend Issues:** Check browser console (F12)
- **API Issues:** Visit http://localhost:5000/api/health
- **Documentation:** See README.md in backend-python/

---

**Enjoy using File Converter Pro! 🎉**

*Transparent • Reproducible • Private*
