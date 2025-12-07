# Frontend Setup & Usage Guide

## 📋 Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend running on `http://localhost:5000`

### Installation

```bash
cd converter/frontend
npm install
```

### Development Mode

```bash
# Start React dev server (http://localhost:3000)
npm start

# The app will automatically reload when you make changes
```

### Production Build

```bash
npm run build

# Output goes to: converter/frontend/build/
# Ready for deployment
```

## 🎨 UI Components

### 1. **FileUploader** (`src/components/FileUploader.jsx`)
- Drag-and-drop file upload
- 500MB file size limit
- Displays file info (name, size, type)
- Shows supported formats
- Clear/remove file option

**Features:**
- Real-time file validation
- Visual feedback on hover/drag
- Format compatibility hints

### 2. **ConversionPanel** (`src/components/ConversionPanel.jsx`)
- Output format selection
- Quality slider (0-100%)
- Advanced options toggle
- Real-time conversion button
- Feature highlights

**Features:**
- Smart format suggestions based on input file
- Image quality optimization
- Advanced compression options
- Disabled state during conversion

### 3. **HistoryPanel** (`src/components/HistoryPanel.jsx`)
- Conversion history with timestamps
- Expandable conversion details
- Quality metrics display
- Download converted files
- Recipe viewer
- Remove history items

**Features:**
- Persistent history (stores in component state)
- Quality score visualization
- Complete audit trail access
- Batch operations

### 4. **HealthCheck** (`src/components/HealthCheck.jsx`)
- Real-time backend connection status
- Fixed position indicator
- Auto-refresh every 30 seconds
- Status: Connected/Disconnected/Checking

## 🔌 API Integration

### Supported Endpoints

```
Image Conversions:
POST /api/conversions/image
  - Input: JPG, PNG, WebP, GIF, BMP, TIFF
  - Output: Any supported format
  - Query params: quality

Document Conversions:
POST /api/conversions/document/csv-to-excel
POST /api/conversions/document/excel-to-csv
POST /api/conversions/document/csv-to-parquet

Generic Conversion:
POST /api/convert
  - Handles any supported format pair

Info Endpoints:
GET /api/health - Backend status
GET /api/formats - List all supported formats
```

### Request/Response Example

```javascript
// Request
POST /api/conversions/image
Content-Type: multipart/form-data

file: <binary>
output_format: "webp"
quality: "85"

// Response
{
  "success": true,
  "output_format": "webp",
  "file_size": 1024000,
  "quality": {
    "ssim": 0.92,
    "compression_ratio": 0.45
  },
  "recipe": {...}
}
```

## 🎯 Usage Workflow

### Step 1: Upload File
1. Drag file to dropzone OR click to browse
2. File appears with details (name, size, type)

### Step 2: Select Output Format
1. Available formats dynamically load based on input type
2. Click desired format button to select

### Step 3: Adjust Settings (Optional)
1. For images: Use quality slider (0-100%)
2. Click "Advanced Options" for additional settings:
   - Preserve metadata
   - Keep original colors
   - Enable compression

### Step 4: Convert
1. Click "Convert Now" button
2. Monitor progress with visual feedback
3. Wait for "Conversion completed successfully!" message

### Step 5: Download & Manage
1. Click "Download" in history to save file
2. Click "View Recipe" to see complete audit trail
3. Click "Remove" to delete from history

## 🚀 Environment Variables

Create `.env` file in `converter/frontend/`:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:5000/api

# Optional: Enable debug logging
REACT_APP_DEBUG=true
```

## 📱 Responsive Design

The UI is fully responsive for:
- Desktop (1200px+)
- Tablet (768px - 1200px)
- Mobile (< 768px)

On mobile devices:
- Single column layout
- Touch-optimized buttons
- Simplified header
- Full-width components

## 🔧 Customization

### Change Color Scheme

Edit `src/App.css`:
```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Modify Layout

Edit `src/App.css`:
```css
.grid {
  /* Default: 3 columns */
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  
  /* For 2 columns: */
  grid-template-columns: repeat(2, 1fr);
}
```

### Add New Components

1. Create file: `src/components/NewComponent.jsx`
2. Create styles: `src/components/NewComponent.css`
3. Import in `App.jsx`: `import NewComponent from './components/NewComponent'`
4. Add to JSX: `<NewComponent />`

## 🐛 Troubleshooting

### "Backend Disconnected" Error
- **Cause:** Flask backend not running
- **Fix:** Start backend: `python app.py`
- **Check:** Visit `http://localhost:5000/api/health`

### "File Upload Failed" Error
- **Cause:** File size > 500MB or network issue
- **Fix:** Reduce file size or check connection
- **Limit:** Max 500MB (configurable in backend)

### "No Conversion History"
- **Cause:** History stored in component state (clears on refresh)
- **Fix:** Implement localStorage persistence (optional enhancement)

### Styles Not Loading
- **Cause:** CSS files not imported
- **Fix:** Verify imports at top of each component
- **Check:** Browser DevTools → Sources tab

### CORS Errors
- **Cause:** Backend CORS not configured
- **Fix:** Backend already has CORS enabled
- **Verify:** Check `app.py` has `CORS(app)`

## 📦 Dependencies

- **react** (18.2.0) - UI framework
- **axios** (1.6.0) - HTTP client
- **react-dropzone** (14.2.3) - File upload
- **react-icons** (4.11.0) - Icon library
- **lucide-react** (0.263.1) - Additional icons
- **zustand** (4.4.0) - State management (optional, not yet used)

## 🔐 Security Features

- Secure file upload validation
- XSS prevention through React
- CORS headers properly configured
- File size limits enforced
- Safe filename handling

## 📊 Performance Tips

1. **Lazy load components** for large apps
2. **Memoize expensive calculations** with `useMemo`
3. **Use production build** for deployment
4. **Enable gzip compression** on server
5. **CDN cache static assets** for faster load

## 🚢 Deployment

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY converter/frontend .
RUN npm install && npm run build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

### Netlify/Vercel
1. Connect GitHub repo
2. Set build command: `npm run build`
3. Set output directory: `build`
4. Add env variable: `REACT_APP_API_URL`

### Traditional Server
```bash
npm run build
# Serve converter/frontend/build/ with static file server
```

## 📝 Next Steps

1. ✅ Start backend: `python app.py` in `backend-python/`
2. ✅ Install dependencies: `npm install`
3. ✅ Start frontend: `npm start`
4. ✅ Open `http://localhost:3000`
5. ✅ Try converting a file!

## 🆘 Support

- Backend logs: Check `backend-python/` console
- Frontend logs: Check browser console (F12)
- API documentation: See `QUICKSTART.md`

---

**Happy Converting! 🎉**
