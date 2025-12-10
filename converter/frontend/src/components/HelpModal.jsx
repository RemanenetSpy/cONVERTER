
import React, { useState, useMemo } from 'react';
import { X, Search, Book, Shield, FileText, Zap, HelpCircle } from 'lucide-react';
import './HelpModal.css';

const TABS = [
    { id: 'start', label: 'Getting Started', icon: <Zap size={18} /> },
    { id: 'features', label: 'Audit & Recipes', icon: <Book size={18} /> },
    { id: 'formats', label: 'Formats', icon: <FileText size={18} /> },
    { id: 'privacy', label: 'Privacy', icon: <Shield size={18} /> },
    { id: 'faq', label: 'FAQ', icon: <HelpCircle size={18} /> },
];

const CONTENT = {
    start: {
        title: "How to Use Converter Pro",
        items: [
            {
                q: "1. Upload a File",
                a: "Drag & drop your file or click to browse. We support documents (PDF, DOCX), images (PNG, HEIC), and archives."
            },
            {
                q: "2. Choose Options",
                a: "Select your desired output format. For images, you can adjust quality. For PDFs, you can convert to Word or Excel."
            },
            {
                q: "3. Convert & Download",
                a: "Click 'Convert Now'. Once finished, your file appears in the History panel below for download."
            },
            {
                q: "4. Replay from Recipe",
                a: "Want the exact same settings? Click 'Load Recipe' in the panel and upload a previous .json recipe file."
            }
        ]
    },
    features: {
        title: "Audit Trails & Reproducibility",
        items: [
            {
                q: "What is a Recipe?",
                a: "Every conversion generates a 'Recipe' - a JSON file containing all settings, timestamps, and file checksums used in the process."
            },
            {
                q: "Verifying Integrity",
                a: "You can download the Recipe from the History panel. It contains SHA-256 hashes of both input and output files, proving they haven't been tampered with."
            },
            {
                q: "Reproducible Builds",
                a: "To repeat a conversion exactly, simply upload its Recipe file. The app will auto-configure all settings to match the original job."
            }
        ]
    },
    formats: {
        title: "Supported File Formats",
        items: [
            {
                q: "Documents",
                a: "PDF, DOCX, DOC, XLSX, XLS, CSV, PARQUET, JSON, PPTX"
            },
            {
                q: "Images",
                a: "JPG, PNG, WEBP, GIF, BMP, TIFF, SVG, HEIC"
            },
            {
                q: "Audio",
                a: "MP3, WAV, AAC, OGG, M4A"
            },
            {
                q: "Archives",
                a: "ZIP, TAR, 7Z"
            }
        ]
    },
    privacy: {
        title: "Privacy & Security",
        items: [
            {
                q: "Ephemeral Processing",
                a: "Your files are processed on a secure server and deleted immediately after conversion. We do not store your data."
            },
            {
                q: "Auto-Cleanup",
                a: "As a fallback safety measure, a background sweeper permanently erases any residual files every 30 minutes."
            },
            {
                q: "Local Logging",
                a: "We do not use third-party analytics trackers. All logs are local and anonymized."
            }
        ]
    },
    faq: {
        title: "Frequently Asked Questions",
        items: [
            {
                q: "Is it free?",
                a: "Yes, Converter Pro is completely free and open source."
            },
            {
                q: "Why is my file upload failing?",
                a: "Check if your file exceeds the 500MB limit. Also ensure you have a stable internet connection."
            },
            {
                q: "Can I convert video?",
                a: "Not yet. Video conversion is planned for a future update."
            },
            {
                q: "I found a bug, how do I report it?",
                a: "Use the floating 'Feedback' button in the bottom right corner to send us a bug report directly."
            }
        ]
    }
};

function HelpModal({ isOpen, onClose }) {
    const [activeTab, setActiveTab] = useState('start');
    const [searchQuery, setSearchQuery] = useState('');

    const filteredContent = useMemo(() => {
        if (!isOpen) return []; // optimization
        if (!searchQuery) return CONTENT[activeTab].items;

        // Search across ALL tabs if query exists
        const allItems = Object.values(CONTENT).flatMap(c => c.items);
        return allItems.filter(item =>
            item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.a.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [activeTab, searchQuery, isOpen]);

    if (!isOpen) return null;

    return (
        <div className="help-modal-overlay" onClick={onClose}>
            <div className="help-modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true">

                {/* Header */}
                <div className="help-header">
                    <h2>📘 User Guide & Help</h2>
                    <button className="close-btn" onClick={onClose} aria-label="Close help">
                        <X size={24} />
                    </button>
                </div>

                <div className="help-body">
                    {/* Sidebar Navigation */}
                    <div className="help-sidebar">
                        <div className="help-search">
                            <Search size={16} />
                            <input
                                type="text"
                                placeholder="Search..."
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                            />
                        </div>

                        <nav className="help-nav">
                            {TABS.map(tab => (
                                <button
                                    key={tab.id}
                                    className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                                    onClick={() => { setActiveTab(tab.id); setSearchQuery(''); }}
                                >
                                    {tab.icon}
                                    <span>{tab.label}</span>
                                </button>
                            ))}
                        </nav>
                    </div>

                    {/* Content Area */}
                    <div className="help-content">
                        {searchQuery ? (
                            <h3>Searching for "{searchQuery}"</h3>
                        ) : (
                            <h3>{CONTENT[activeTab].title}</h3>
                        )}

                        <div className="help-items">
                            {filteredContent.length > 0 ? (
                                filteredContent.map((item, idx) => (
                                    <div key={idx} className="help-item">
                                        <h4>{item.q}</h4>
                                        <p>{item.a}</p>
                                    </div>
                                ))
                            ) : (
                                <p className="no-results">No results found.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default HelpModal;
