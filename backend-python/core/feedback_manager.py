
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Manages user feedback storage (Privacy-First: Local JSON)"""
    
    FEEDBACK_DIR = "./feedback"
    
    @classmethod
    def save_feedback(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save feedback to a daily JSON line file"""
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
                
            return {"success": True, "id": entry["id"]}
            
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise e
