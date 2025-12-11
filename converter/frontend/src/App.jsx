import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import './components/Enhancements.css';
import './components/MobileOptimizations.css';
import './components/TrendingPatterns.css';
import FileUploader from './components/FileUploader';
import ConversionPanel from './components/ConversionPanel';
import HistoryPanel from './components/HistoryPanel';
import HealthCheck from './components/HealthCheck';
import FeedbackWidget from './components/FeedbackWidget';
import HelpModal from './components/HelpModal';
import { getFormatIcon } from './utils/formatUtils';
import { getSmartSuggestion, detectUseCase, getApplicableTemplates } from './utils/smartSuggestions';
import { HelpCircle } from 'lucide-react';
import Cube3D from './components/Cube3D';

// In production (Render), we serve frontend from same origin, so use relative path '/api'
// In development, we use localhost:5000
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? '/api'
  : (process.env.REACT_APP_API_URL || 'http://localhost:5000/api');

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('unknown');
  const [supportedFormats, setSupportedFormats] = useState({});
  const [progress, setProgress] = useState(0);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  // Load conversions from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('conversions');
    if (saved) {
      try {
        setConversions(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load saved conversions:', e);
      }
    }
  }, []);

  // Use system dark mode preference
  useEffect(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.body.className = prefersDark ? 'dark-mode' : 'light-mode';

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      document.body.className = e.matches ? 'dark-mode' : 'light-mode';
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        document.querySelector('.history-panel')?.scrollIntoView({ behavior: 'smooth' });
      }
      if (e.key === 'Escape') {
        setSelectedFile(null);
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Save conversions to localStorage whenever they change
  useEffect(() => {
    if (conversions.length > 0) {
      localStorage.setItem('conversions', JSON.stringify(conversions));
    }
  }, [conversions]);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    fetchSupportedFormats();
    const interval = setInterval(checkApiHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setApiStatus(response.data.status === 'ok' ? 'connected' : 'error');
    } catch (error) {
      setApiStatus('disconnected');
    }
  };

  const fetchSupportedFormats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/formats`);
      setSupportedFormats(response.data);
    } catch (error) {
      console.error('Failed to fetch formats:', error);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };

  const handleConversion = async (outputFormat, options = {}) => {
    if (!selectedFile) {
      alert('Please select a file first');
      return;
    }

    setLoading(true);
    setProgress(0);
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Handle compression mode
    if (outputFormat === 'compress' && options.endpoint) {
      formData.append('quality', options.quality || 85);

      try {
        const response = await axios.post(
          `${API_BASE_URL}/compress/${options.endpoint}`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setProgress(percentCompleted);
            }
          }
        );

        const conversion = {
          id: Date.now(),
          fileName: selectedFile.name,
          outputFormat: 'compressed',
          outputFileName: response.data.outputFileName || `compressed_${selectedFile.name}`,
          status: 'completed',
          timestamp: new Date().toISOString(),
          originalSize: response.data.originalSize,
          compressedSize: response.data.compressedSize,
          reductionPercent: response.data.reductionPercent,
          size: response.data.output?.size || 0,
          recipe: response.data.recipe || null
        };

        setConversions([conversion, ...conversions]);
        alert(`✅ File compressed by ${response.data.reductionPercent}%!`);
        setSelectedFile(null);
      } catch (error) {
        console.error('Compression failed:', error);
        const errorMsg = error.response?.data?.error || error.message || 'Unknown error';
        alert(`❌ Compression failed: ${errorMsg}`);
      } finally {
        setLoading(false);
        setProgress(0);
      }
      return;
    }

    // Regular conversion
    formData.append('format', outputFormat);

    // Add quality parameter for images
    if (options.quality) {
      formData.append('quality', options.quality);
    }

    try {
      const endpoint = getEndpointForFormat(selectedFile.name, outputFormat);
      const response = await axios.post(
        `${API_BASE_URL}${endpoint}`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        }
      );

      const conversion = {
        id: Date.now(),
        fileName: selectedFile.name,
        outputFormat,
        outputFileName: response.data.outputFileName || `converted.${outputFormat}`,
        status: 'completed',
        timestamp: new Date().toISOString(),
        quality: response.data.quality || {},
        recipe: response.data.recipe || null,
        size: response.data.output?.size || 0
      };

      setConversions([conversion, ...conversions]);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      alert('✅ Conversion completed successfully!');
      setSelectedFile(null); // Clear selection after successful conversion
    } catch (error) {
      console.error('Conversion failed:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Unknown error';
      alert(`❌ Conversion failed: ${errorMsg}`);
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const handleDownload = async (fileName) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/download/${fileName}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('❌ Download failed. File may have expired.');
    }
  };

  const getEndpointForFormat = (fileName, outputFormat) => {
    const ext = fileName.split('.').pop().toLowerCase();

    // PDF conversions
    if (ext === 'pdf') {
      if (outputFormat === 'docx') return '/conversions/pdf/to-word';
      if (outputFormat === 'xlsx') return '/conversions/pdf/to-excel';
    }
    if (ext === 'docx' && outputFormat === 'pdf') return '/conversions/word/to-pdf';
    if (ext === 'xlsx' && outputFormat === 'pdf') return '/conversions/excel/to-pdf';

    // JSON conversions
    if (ext === 'csv' && outputFormat === 'json') return '/conversions/csv/to-json';
    if (ext === 'json' && outputFormat === 'csv') return '/conversions/json/to-csv';

    // Image conversions
    if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'svg', 'heic'].includes(ext)) {
      // Image to PDF
      if (outputFormat === 'pdf') return '/conversions/image/to-pdf';
      // Image to image
      return '/conversions/image';
    }

    // Document conversions
    if (ext === 'xlsx' || ext === 'xls') {
      if (outputFormat === 'csv') return '/conversions/document/excel-to-csv';
    }
    if (ext === 'csv') {
      if (outputFormat === 'xlsx') return '/conversions/document/csv-to-excel';
      if (outputFormat === 'parquet') return '/conversions/document/csv-to-parquet';
    }

    return '/convert';
  };

  return (
    <div className="app">
      <HealthCheck status={apiStatus} />


      {/* Success Animation */}
      {showSuccess && (
        <div className="success-overlay">
          <div className="success-checkmark"></div>
        </div>
      )}

      <div className="app-container">

        {/* Fixed Guide Button */}
        <button
          className="help-btn-fixed"
          onClick={() => setShowHelp(true)}
          aria-label="Open Guide"
        >
          <HelpCircle size={20} /> Guide
        </button>

        {/* Hero Section */}
        <header className="app-hero">
          <Cube3D />
          <h1 className="hero-title">File Converter Pro</h1>
          <p className="hero-subtitle">Transparent • Reproducible • Privacy-First</p>
        </header>

        <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />

        <main className="app-main">
          {/* ... grid content ... */}
          <div className="grid">
            <div className="column">
              <FileUploader
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                supportedFormats={supportedFormats}
              />
            </div>

            <div className="column">
              <ConversionPanel
                selectedFile={selectedFile}
                supportedFormats={supportedFormats}
                onConvert={handleConversion}
                loading={loading}
                progress={progress}
              />
            </div>

            <div className="column full-width">
              <HistoryPanel
                conversions={conversions}
                onRemove={(id) => {
                  setConversions(conversions.filter(c => c.id !== id));
                }}
              />
            </div>
          </div>
        </main>

        {/* Unified Modern Footer */}
        <footer className="app-footer-modern">
          <div className="footer-mission">
            <p>
              Your files never leave your control. Processed in memory, deleted immediately.
              <br />
              <span className="footer-sub">Open source • Reproducible • Zero-knowledge architecture</span>
            </p>
          </div>
          <div className="footer-bottom">
            <p>© 2025 Converter Pro • Quality Guaranteed</p>
          </div>
        </footer>
      </div>

      <FeedbackWidget />
    </div>
  );
}

export default App;
