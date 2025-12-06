# File Size Limits Configuration (Free Tier Optimized)

## Resource-Aware File Size Limits

Based on free tier constraints (Render.com free tier: 512MB RAM, 15min timeout):

### Image Files
- **JPEG/PNG/WebP/GIF/BMP**: 50 MB max
- **TIFF**: 30 MB max (uncompressed format)
- **SVG**: 10 MB max (text-based, fast processing)
- **HEIC**: 50 MB max (iPhone photos)
- **RAW formats**: Not supported (too resource-intensive)

### Document Files
- **PDF**: 100 MB max (complex rendering)
- **Word (DOCX/DOC)**: 50 MB max
- **Excel (XLSX/XLS)**: 50 MB max
- **PowerPoint (PPTX/PPT)**: 100 MB max
- **CSV**: 100 MB max (simple text processing)
- **JSON**: 50 MB max
- **Parquet**: 100 MB max (compressed format)

### Video Files (Limited Support)
- **MP4/WebM/AVI/MOV**: 50 MB max
- **Video → GIF**: 20 MB max (memory intensive)
- **Video → Audio**: 100 MB max (audio extraction is lightweight)
- **Note**: Video conversions disabled for files >50MB to prevent crashes

### Audio Files
- **MP3/WAV/AAC/OGG/M4A**: 50 MB max
- **FLAC**: 100 MB max (lossless, but efficient)

### Archive Files
- **ZIP/7Z/TAR**: 200 MB max (compression/decompression)

## Implementation Strategy

### Backend Validation
```python
FILE_SIZE_LIMITS = {
    # Images
    'jpg': 50 * 1024 * 1024,
    'jpeg': 50 * 1024 * 1024,
    'png': 50 * 1024 * 1024,
    'webp': 50 * 1024 * 1024,
    'gif': 50 * 1024 * 1024,
    'bmp': 50 * 1024 * 1024,
    'tiff': 30 * 1024 * 1024,
    'svg': 10 * 1024 * 1024,
    'heic': 50 * 1024 * 1024,
    
    # Documents
    'pdf': 100 * 1024 * 1024,
    'docx': 50 * 1024 * 1024,
    'doc': 50 * 1024 * 1024,
    'xlsx': 50 * 1024 * 1024,
    'xls': 50 * 1024 * 1024,
    'pptx': 100 * 1024 * 1024,
    'ppt': 100 * 1024 * 1024,
    'csv': 100 * 1024 * 1024,
    'json': 50 * 1024 * 1024,
    'parquet': 100 * 1024 * 1024,
    
    # Video (limited)
    'mp4': 50 * 1024 * 1024,
    'webm': 50 * 1024 * 1024,
    'avi': 50 * 1024 * 1024,
    'mov': 50 * 1024 * 1024,
    
    # Audio
    'mp3': 50 * 1024 * 1024,
    'wav': 50 * 1024 * 1024,
    'aac': 50 * 1024 * 1024,
    'ogg': 50 * 1024 * 1024,
    'm4a': 50 * 1024 * 1024,
    'flac': 100 * 1024 * 1024,
    
    # Archives
    'zip': 200 * 1024 * 1024,
    '7z': 200 * 1024 * 1024,
    'tar': 200 * 1024 * 1024
}

def validate_file_size(filename, file_size):
    ext = filename.split('.')[-1].lower()
    limit = FILE_SIZE_LIMITS.get(ext, 50 * 1024 * 1024)  # Default 50MB
    
    if file_size > limit:
        limit_mb = limit / (1024 * 1024)
        raise ValueError(f"File too large. Maximum size for {ext.upper()} files is {limit_mb}MB")
    
    return True
```

### Frontend Display
- Show file size limits in FileUploader
- Display warning if file exceeds limit
- Suggest compression for oversized files

## Rationale

### Memory Constraints
- Free tier: 512MB RAM
- Leave 256MB for system/overhead
- Max 256MB for file processing
- Safety margin: Use 50-100MB limits

### Processing Time
- Free tier: 15min timeout
- Target: <2min per conversion
- Video: Most resource-intensive (50MB limit)
- Images/Documents: Fast (<30s for 50MB)

### Storage Constraints
- Ephemeral storage on free tier
- Files deleted after 24h inactivity
- Keep conversions lightweight

## User Communication

**Error Messages:**
- "File too large. Maximum size for PDF files is 100MB. Try compressing first."
- "Video files are limited to 50MB on free tier. Consider using our compression tool first."
- "For files larger than 200MB, please upgrade to premium tier."

**Recommendations:**
- Suggest compression before conversion
- Offer batch processing for multiple small files
- Guide users to optimize before upload
