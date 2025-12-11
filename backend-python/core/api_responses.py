"""
Utility functions for standardized API responses
"""
from flask import jsonify
from typing import Dict, Any, Optional


def success_response(data: Dict[str, Any], message: Optional[str] = None, status_code: int = 200):
    """Standardized success response"""
    response = {"success": True}
    if message:
        response["message"] = message
    response.update(data)
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
    """Standardized error response"""
    response = {
        "success": False,
        "error": message
    }
    if details:
        response["details"] = details
    return jsonify(response), status_code


def validation_error(message: str, field: Optional[str] = None):
    """Validation error response (400)"""
    details = {"field": field} if field else None
    return error_response(message, 400, details)
