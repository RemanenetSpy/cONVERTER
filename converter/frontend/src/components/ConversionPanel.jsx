import React, { useState, useMemo } from 'react';
import { Zap, Settings } from 'lucide-react';
import './ConversionPanel.css';

function ConversionPanel({ selectedFile, supportedFormats, onConvert, loading, progress }) {
  const [selectedFormat, setSelectedFormat] = useState('');
  const [quality, setQuality] = useState(95);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [compressionMode, setCompressionMode] = useState(false);

  const availableFormats = useMemo(() => {
    if (!selectedFile) return [];

    const inputExt = selectedFile.name.split('.').pop().toLowerCase();

    // Comprehensive format mapping
    const formatMap = {
      'jpg': ['png', 'webp', 'gif', 'bmp', 'tiff', 'pdf'],
      'jpeg': ['png', 'webp', 'gif', 'bmp', 'tiff', 'pdf'],
      'png': ['jpg', 'webp', 'gif', 'bmp', 'tiff', 'pdf'],
      'webp': ['jpg', 'png', 'gif', 'bmp', 'tiff'],
      'gif': ['jpg', 'png', 'webp', 'bmp', 'tiff'],
      'bmp': ['jpg', 'png', 'webp', 'gif', 'tiff'],
      'tiff': ['jpg', 'png', 'webp', 'gif', 'bmp'],
      'svg': ['png', 'jpg'],
      'heic': ['jpg', 'png'],
      'pdf': ['docx', 'xlsx'],
      'docx': ['pdf'],
      'doc': ['pdf', 'docx'],
      'xlsx': ['csv', 'json', 'parquet', 'pdf'],
      'xls': ['csv', 'xlsx', 'pdf'],
      'csv': ['xlsx', 'json', 'parquet'],
      'json': ['csv', 'xlsx'],
      'parquet': ['csv', 'xlsx'],
      'mp3': ['wav', 'aac', 'ogg'],
      'wav': ['mp3', 'aac'],
      'aac': ['mp3', 'wav'],
      'ogg': ['mp3', 'wav'],
      'm4a': ['mp3', 'wav'],
      'zip': ['7z', 'tar'],
      '7z': ['zip'],
      'tar': ['zip']
    };

    return formatMap[inputExt] || [];
  }, [selectedFile]);

  const supportsCompression = useMemo(() => {
    if (!selectedFile) return false;
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    return ['jpg', 'jpeg', 'png', 'webp', 'pdf', 'xlsx', 'csv'].includes(ext);
  }, [selectedFile]);

  const handleConvert = () => {
    if (!compressionMode && !selectedFormat) {
      alert('⚠️ Please select an output format first!');
      return;
    }

    const options = {
      quality: quality,
    };

    if (compressionMode) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
        options.endpoint = 'image';
      } else if (ext === 'pdf') {
        options.endpoint = 'pdf';
      } else {
        alert('⚠️ Compression not supported for this file type yet');
        return;
      }
    }

    onConvert(compressionMode ? 'compress' : selectedFormat, options);
  };

  return (
    <div className="conversion-panel card">
      <h2>⚙️ {compressionMode ? 'Compress' : 'Convert'}</h2>

      {/* Recipe Loader */}
      <div className="recipe-loader">
        <label htmlFor="recipe-upload" className="recipe-btn" title="Load settings from a previous recipe">
          <Settings size={16} /> Load Recipe
        </label>
        <input
          id="recipe-upload"
          type="file"
          accept=".json,.yaml,.yml"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
              try {
                const recipe = JSON.parse(event.target.result);
                // Auto-configure UI from recipe
                if (recipe.output && recipe.output.format) {
                  setSelectedFormat(recipe.output.format);
                  if (recipe.output.parameters && recipe.output.parameters.quality) {
                    setQuality(recipe.output.parameters.quality);
                  }
                  alert(`✅ Recipe Loaded: Set format to ${recipe.output.format.toUpperCase()}`);
                }
              } catch (err) {
                alert('❌ Invalid Recipe File');
              }
            };
            reader.readAsText(file);
          }}
        />
      </div>

      {supportsCompression && (
        <div className="mode-toggle">
          <button
            className={!compressionMode ? 'active' : ''}
            onClick={() => { setCompressionMode(false); setSelectedFormat(''); }}
          >
            Convert Format
          </button>
          <button
            className={compressionMode ? 'active' : ''}
            onClick={() => { setCompressionMode(true); setSelectedFormat(''); }}
          >
            Reduce Size
          </button>
        </div>
      )}

      {!compressionMode && (

        <div className="conversion-section">
          <label className="section-label">
            Output Format {selectedFormat && `(${selectedFormat.toUpperCase()})`}
          </label>
          <div className="format-select-grid">
            {availableFormats.length > 0 ? (
              availableFormats.map((format) => (
                <button
                  key={format}
                  className={`format-btn ${selectedFormat === format ? 'active' : ''}`}
                  onClick={() => setSelectedFormat(format)}
                  disabled={loading}
                >
                  {format.toUpperCase()}
                </button>
              ))
            ) : (
              <p className="no-formats">
                {selectedFile
                  ? '⚠️ No compatible formats available for this file type'
                  : '📁 Select a file first to see available formats'}
              </p>
            )}
          </div>
        </div>
      )}

      {selectedFile && selectedFile.type.startsWith('image/') && (
        <div className="conversion-section">
          <label className="section-label">
            Quality: <span className="quality-value">{quality}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={quality}
            onChange={(e) => setQuality(parseInt(e.target.value))}
            className="quality-slider"
            disabled={loading}
          />
          <div className="quality-info">
            <span>Lower (Smaller file)</span>
            <span>Higher (Better quality)</span>
          </div>
        </div>
      )}

      {loading && progress > 0 && (
        <div className="progress-section">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="progress-text">{progress === 100 ? 'Processing...' : `${progress}% uploaded`}</p>
        </div>
      )}

      <button
        className="convert-btn"
        onClick={handleConvert}
        disabled={!selectedFile || (!compressionMode && !selectedFormat) || loading}
      >
        <Zap size={20} />
        {loading ? (
          progress === 100 ? 'Processing...' : `Uploading... ${progress}%`
        ) : (
          compressionMode ? 'Compress File' : 'Convert Now'
        )}
      </button>

      <div className="info-box">
        <h4>✨ Features</h4>
        <ul>
          <li>✓ Quality-assured conversions</li>
          <li>✓ Automatic integrity checks</li>
          <li>✓ Complete audit trail (YAML recipes)</li>
          <li>✓ Privacy-first processing</li>
        </ul>
      </div>
    </div>
  );
}

export default ConversionPanel;
