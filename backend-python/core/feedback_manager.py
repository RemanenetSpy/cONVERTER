
import os
import json
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Manages user feedback storage (Privacy-First: Local JSON + Email)"""
    
    FEEDBACK_DIR = "./feedback"
    
    @classmethod
    def _send_email_notification(cls, feedback_data: Dict[str, Any]) -> bool:
        """Send email notification for new feedback"""
        try:
            # Check if email is configured
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            admin_email = os.getenv("ADMIN_EMAIL")
            
            if not all([smtp_server, smtp_user, smtp_password, admin_email]):
                logger.info("Email notifications not configured (missing env vars)")
                return False
            
            # Create email
            msg = EmailMessage()
            msg['Subject'] = f"New {feedback_data.get('type', 'feedback').title()} - Converter App"
            msg['From'] = smtp_user
            msg['To'] = admin_email
            
            # Email body
            body = f"""
New Feedback Received
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: {feedback_data.get('type', 'general').upper()}
Time: {feedback_data.get('timestamp', 'N/A')}

Message:
{feedback_data.get('message', 'No message')}

Contact: {feedback_data.get('email', 'Anonymous')}

Metadata:
- User Agent: {feedback_data.get('metadata', {}).get('userAgent', 'Unknown')}
- Page: {feedback_data.get('metadata', {}).get('page', '/')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feedback ID: {feedback_data.get('id', 'N/A')}
"""
            msg.set_content(body)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent for feedback {feedback_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @classmethod
    def save_feedback(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save feedback to a daily JSON line file + send email"""
        try:
            os.makedirs(cls.FEEDBACK_DIR, exist_ok=True)
            
            # Create a localized timestamp
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Structure the entry
            entry = {
                "id": f"fb_{int(datetime.utcnow().timestamp())}",
                "timestamp": timestamp,
                "type": data.get("type", "general"), # bug, feature, general
                "message": data.get("message", ""),
                "email": data.get("email", "anonymous"),
                "metadata": {
                    "userAgent": data.get("userAgent", "unknown"),
                    "page": data.get("page", "/"),
                    "version": "1.0.0"
                }
            }
            
            # Save to daily file (simple rotation)
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            filename = os.path.join(cls.FEEDBACK_DIR, f"feedback_{date_str}.jsonl")
            
            with open(filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            
            # Send email notification (non-blocking - doesn't fail if email fails)
            cls._send_email_notification(entry)
                
            return {"success": True, "id": entry["id"]}
            
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise e
