import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import './FileUploader.css';

function FileUploader({ onFileSelect, selectedFile, supportedFormats = {} }) {
  const onDrop = useCallback((acceptedFiles, fileRejections) => {
    // Handle rejected files (Too large, etc)
    if (fileRejections.length > 0) {
      const rejection = fileRejections[0];
      const errorMsg = rejection.errors[0]?.message || "File rejected";
      alert(`⚠️ Cannot upload file: ${errorMsg}`);
      return;
    }

    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    validator: (file) => {
      const ext = file.name.split('.').pop().toLowerCase();
      // Limits in Bytes (matching backend app.py)
      const limits = {
        'jpg': 50, 'jpeg': 50, 'png': 50, 'webp': 50, 'gif': 50, 'bmp': 50, 'heic': 50,
        'tiff': 30, 'svg': 10,
        'pdf': 100, 'docx': 50, 'doc': 50, 'xlsx': 50, 'xls': 50,
        'csv': 100, 'json': 50, 'parquet': 100,
        'mp3': 50, 'wav': 50, 'aac': 50, 'ogg': 50, 'm4a': 50,
        'zip': 200, '7z': 200, 'tar': 200
      };

      const limitMB = limits[ext] || 50; // Default 50MB
      if (file.size > limitMB * 1024 * 1024) {
        return {
          code: "file-too-large",
          message: `File is larger than ${limitMB}MB`
        };
      }
      return null;
    }
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleClear = () => {
    onFileSelect(null);
  };

  return (
    <div className="file-uploader">
      <h2>📁 Select File</h2>

      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <Upload size={48} />
          <p className="dropzone-primary">
            {isDragActive
              ? 'Drop your file here...'
              : 'Drag & drop a file here'}
          </p>
          <p className="dropzone-secondary">or click to browse</p>
          <p className="dropzone-note">Max file size: 500 MB</p>
        </div>
      </div>

      {selectedFile && (
        <div className="file-info">
          <div className="file-details">
            <File size={20} />
            <div>
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{formatFileSize(selectedFile.size)}</p>
              <p className="file-type">{selectedFile.type || 'Unknown type'}</p>
            </div>
          </div>
          <button className="clear-btn" onClick={handleClear} title="Remove file">
            <X size={20} />
          </button>
        </div>
      )}

      <div className="supported-formats">
        <h3>📋 Supported Formats</h3>
        <div className="format-grid">
          {Object.keys(supportedFormats || {}).length === 0 ? (
            <div className="no-formats">No formats available</div>
          ) : (
            (() => {
              const keys = Object.keys(supportedFormats);
              return (
                <>
                  {keys.slice(0, 8).map((format) => (
                    <span key={format} className="format-badge">
                      {format.toUpperCase()}
                    </span>
                  ))}
                  {keys.length > 8 && (
                    <span className="format-badge">+{keys.length - 8}</span>
                  )}
                </>
              );
            })()
          )}
        </div>
      </div>
    </div>
  );
}

export default FileUploader;
