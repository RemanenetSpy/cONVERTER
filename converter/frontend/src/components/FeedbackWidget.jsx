
import React, { useState } from 'react';
import axios from 'axios';
import { MessageSquare, X, Send, AlertCircle, CheckCircle } from 'lucide-react';
import './FeedbackWidget.css';

const API_BASE_URL = process.env.NODE_ENV === 'production'
    ? '/api'
    : (process.env.REACT_APP_API_URL || 'http://localhost:5000/api');

function FeedbackWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [type, setType] = useState('general'); // general, bug, feature
    const [message, setMessage] = useState('');
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState('idle'); // idle, sending, success, error

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        setStatus('sending');
        try {
            await axios.post(`${API_BASE_URL}/feedback`, {
                type,
                message,
                email,
                page: window.location.pathname
            });
            setStatus('success');
            setTimeout(() => {
                setIsOpen(false);
                setMessage('');
                setEmail('');
                setStatus('idle');
            }, 2000);
        } catch (error) {
            console.error('Feedback failed:', error);
            setStatus('error');
        }
    };

    return (
        <div className={`feedback-widget ${isOpen ? 'open' : ''}`}>
            {/* Toggle Button */}
            {!isOpen && (
                <button
                    className="feedback-toggle"
                    onClick={() => setIsOpen(true)}
                    title="Send Feedback"
                    aria-label="Open feedback form"
                >
                    <MessageSquare size={24} />
                    <span className="feedback-label">Feedback</span>
                </button>
            )}

            {/* Form Container */}
            {isOpen && (
                <div className="feedback-form-container" role="dialog" aria-modal="true" aria-labelledby="feedback-title">
                    <div className="feedback-header">
                        <h3 id="feedback-title">💬 Send Feedback</h3>
                        <button className="close-btn" onClick={() => setIsOpen(false)} aria-label="Close feedback form">
                            <X size={18} />
                        </button>
                    </div>

                    {status === 'success' ? (
                        <div className="feedback-success">
                            <CheckCircle size={48} color="#48bb78" />
                            <p>Thank you! We received your feedback.</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            <div className="feedback-type-selector" role="group" aria-label="Feedback Type">
                                <button
                                    type="button"
                                    className={type === 'general' ? 'active' : ''}
                                    onClick={() => setType('general')}
                                    aria-pressed={type === 'general'}
                                >
                                    General
                                </button>
                                <button
                                    type="button"
                                    className={type === 'bug' ? 'active' : ''}
                                    onClick={() => setType('bug')}
                                    aria-pressed={type === 'bug'}
                                >
                                    🐞 Bug
                                </button>
                                <button
                                    type="button"
                                    className={type === 'feature' ? 'active' : ''}
                                    onClick={() => setType('feature')}
                                    aria-pressed={type === 'feature'}
                                >
                                    💡 Idea
                                </button>
                            </div>

                            <label htmlFor="feedback-message" className="sr-only">Message</label>
                            <textarea
                                id="feedback-message"
                                placeholder={
                                    type === 'bug' ? "Describe the bug and how to reproduce it..." :
                                        type === 'feature' ? "What feature would you like to see?" :
                                            "Tell us what you think..."
                                }
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                required
                                rows={4}
                            />

                            <input
                                type="email"
                                placeholder="Email (optional, for reply)"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />

                            <button
                                type="submit"
                                className="submit-btn"
                                disabled={status === 'sending' || !message.trim()}
                            >
                                {status === 'sending' ? 'Sending...' : (
                                    <>Send Feedback <Send size={14} /></>
                                )}
                            </button>

                            {status === 'error' && (
                                <p className="error-msg">
                                    <AlertCircle size={12} /> Failed to send. Please try again later.
                                </p>
                            )}
                        </form>
                    )}
                </div>
            )}
        </div>
    );
}

export default FeedbackWidget;
