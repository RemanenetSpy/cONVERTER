import React, { useState } from 'react';
import { Download, Eye, Trash2, ChevronDown } from 'lucide-react';
import './HistoryPanel.css';

// In production (Render), use relative path
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? '/api'
  : (process.env.REACT_APP_API_URL || 'http://localhost:5000/api');

function HistoryPanel({ conversions, onRemove }) {
  const [expandedId, setExpandedId] = useState(null);

  const formatDate = (date) => {
    return new Date(date).toLocaleString();
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleDownload = async (conversion) => {
    try {
      // Download the converted file from backend
      const response = await fetch(`${API_BASE_URL}/download/${conversion.outputFileName}`);

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = conversion.outputFileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('❌ Download failed. File may have been deleted from server.');
    }
  };

  const handleViewRecipe = (conversion) => {
    if (!conversion.recipe) {
      alert('No recipe available for this conversion');
      return;
    }

    // Create a modal or new window to show the YAML recipe
    const recipeWindow = window.open('', '_blank', 'width=600,height=800');
    recipeWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Conversion Recipe - ${conversion.fileName}</title>
          <style>
            body {
              font-family: 'Courier New', monospace;
              padding: 20px;
              background: #1a1a1a;
              color: #f0f0f0;
            }
            h2 {
              color: #667eea;
            }
            pre {
              background: #2d2d2d;
              padding: 20px;
              border-radius: 8px;
              overflow-x: auto;
              white-space: pre-wrap;
              word-wrap: break-word;
            }
            .download-btn {
              background: linear-gradient(135deg, #667eea, #764ba2);
              color: white;
              border: none;
              padding: 10px 20px;
              border-radius: 8px;
              cursor: pointer;
              margin-top: 10px;
            }
            .download-btn:hover {
              opacity: 0.9;
            }
          </style>
        </head>
        <body>
          <h2>📋 Conversion Recipe</h2>
          <p><strong>File:</strong> ${conversion.fileName} → ${conversion.outputFormat.toUpperCase()}</p>
          <p><strong>Date:</strong> ${formatDate(conversion.timestamp)}</p>
          <pre>${JSON.stringify(conversion.recipe, null, 2)}</pre>
          <button class="download-btn" onclick="downloadRecipe()">Download Recipe as YAML</button>
          <script>
            function downloadRecipe() {
              const recipe = ${JSON.stringify(JSON.stringify(conversion.recipe, null, 2))};
              const blob = new Blob([recipe], { type: 'text/yaml' });
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'recipe_${conversion.fileName}.yaml';
              a.click();
              window.URL.revokeObjectURL(url);
            }
          </script>
        </body>
      </html>
    `);
  };

  const handleRemove = (conversionId) => {
    if (window.confirm('Are you sure you want to remove this conversion from history?')) {
      if (onRemove) {
        onRemove(conversionId);
      }
    }
  };

  return (
    <div className="history-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2>📜 Conversion History</h2>
        {conversions.length > 0 && (
          <button
            onClick={() => {
              if (window.confirm('Clear all conversion history?')) {
                if (onRemove) {
                  conversions.forEach(c => onRemove(c.id));
                }
              }
            }}
            style={{
              background: 'rgba(255, 59, 48, 0.2)',
              border: '1px solid rgba(255, 59, 48, 0.5)',
              color: '#ff3b30',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🗑️ Clear All
          </button>
        )}
      </div>

      {conversions.length === 0 ? (
        <div className="empty-state">
          <p>No conversions yet</p>
          <p className="empty-subtext">Start converting files to see history here</p>
        </div>
      ) : (
        <div className="history-list">
          {conversions.map((conversion) => (
            <div key={conversion.id} className="history-item">
              <div
                className="history-header"
                onClick={() => toggleExpand(conversion.id)}
              >
                <div className="history-info">
                  <span className="status-badge completed">✓ Completed</span>
                  <span className="file-name">{conversion.fileName}</span>
                  <span className="arrow">
                    →
                  </span>
                  <span className="output-format">{conversion.outputFormat.toUpperCase()}</span>
                </div>
                <div className="history-time">
                  {formatDate(conversion.timestamp)}
                </div>
                <ChevronDown
                  size={20}
                  className={`expand-icon ${expandedId === conversion.id ? 'expanded' : ''}`}
                />
              </div>

              {expandedId === conversion.id && (
                <div className="history-details">
                  <div className="details-grid">
                    {conversion.quality && Object.keys(conversion.quality).length > 0 && (
                      <div className="detail-section">
                        <h4>Quality Metrics</h4>
                        <div className="metrics">
                          {Object.entries(conversion.quality).map(([key, value]) => (
                            <div key={key} className="metric">
                              <span className="metric-key">{key}:</span>
                              <span className="metric-value">
                                {typeof value === 'number' ? value.toFixed(3) : value}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {conversion.recipe && (
                      <div className="detail-section">
                        <h4>Recipe Available</h4>
                        <p className="recipe-note">
                          Complete audit trail with checksums available
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="action-buttons">
                    <button
                      className="action-btn download-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(conversion);
                      }}
                      title="Download converted file"
                    >
                      <Download size={16} />
                      Download
                    </button>
                    <button
                      className="action-btn view-recipe-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewRecipe(conversion);
                      }}
                      disabled={!conversion.recipe}
                      title={conversion.recipe ? "View YAML recipe" : "No recipe available"}
                    >
                      <Eye size={16} />
                      View Recipe
                    </button>
                    <button
                      className="action-btn delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemove(conversion.id);
                      }}
                      title="Remove from history"
                    >
                      <Trash2 size={16} />
                      Remove
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default HistoryPanel;
