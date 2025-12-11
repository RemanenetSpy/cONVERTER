"""
Flask Backend Server for File Converter
Handles file conversions, recipes, and API endpoints
"""

import os
import asyncio
import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.conversion_engine import ConversionEngine
from core.recipe_manager import RecipeManager
from core.image_converter import ImageConverter
from core.document_converter import DocumentConverter
from core.pdf_converter import PDFConverter
from core.file_size_reducer import FileSizeReducer
from core.audio_converter import AudioConverter
from core.archive_converter import ArchiveConverter
from core.quality_gate import QualityGate
from core.feedback_manager import FeedbackManager

# Initialize Flask app (Static folder pointing to React build)
app = Flask(__name__, static_folder="frontend_build", static_url_path="/")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serve React Frontend
@app.route("/")
def index():
    return send_file(os.path.join(app.static_folder, "index.html"))

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_file(os.path.join(app.static_folder, path))
    return send_file(os.path.join(app.static_folder, "index.html"))

# CORS: allow origins via env var or default to wildcard for dev
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins == "*":
    CORS(app, origins="*", supports_credentials=False)
else:
    CORS(app, origins=allowed_origins.split(","), supports_credentials=True)

# Rate limiter (per-IP)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["60 per minute", "1000 per day"])

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff",
    "csv", "xlsx", "xls", "parquet", "json",
    "docx", "doc", "pptx", "ppt",
    "svg", "heic", "mp3", "wav", "aac", "ogg", "m4a",
    "zip", "tar", "7z"
}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB global max

# File size limits (free tier optimized)
FILE_SIZE_LIMITS = {
    # Images
    'jpg': 50 * 1024 * 1024, 'jpeg': 50 * 1024 * 1024, 'png': 50 * 1024 * 1024,
    'webp': 50 * 1024 * 1024, 'gif': 50 * 1024 * 1024, 'bmp': 50 * 1024 * 1024,
    'tiff': 30 * 1024 * 1024, 'svg': 10 * 1024 * 1024, 'heic': 50 * 1024 * 1024,
    # Documents
    'pdf': 100 * 1024 * 1024, 'docx': 50 * 1024 * 1024, 'doc': 50 * 1024 * 1024,
    'xlsx': 50 * 1024 * 1024, 'xls': 50 * 1024 * 1024, 'csv': 100 * 1024 * 1024,
    'json': 50 * 1024 * 1024, 'parquet': 100 * 1024 * 1024,
    # Audio
    'mp3': 50 * 1024 * 1024, 'wav': 50 * 1024 * 1024, 'aac': 50 * 1024 * 1024,
    'ogg': 50 * 1024 * 1024, 'm4a': 50 * 1024 * 1024,
    # Archives
    'zip': 200 * 1024 * 1024, '7z': 200 * 1024 * 1024, 'tar': 200 * 1024 * 1024
}

def validate_file_size(filename, file_size):
    """Validate file size against format-specific limits"""
    ext = filename.split('.')[-1].lower()
    limit = FILE_SIZE_LIMITS.get(ext, 50 * 1024 * 1024)  # Default 50MB
    
    if file_size > limit:
        limit_mb = limit / (1024 * 1024)
        raise ValueError(f"File too large. Maximum size for {ext.upper()} files is {limit_mb:.0f}MB")
    
    return True

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ----------------------------------------------------
# Privacy: Auto-Cleanup Background Task
# ----------------------------------------------------
import threading
import time

def cleanup_files():
    """Delete files older than 30 minutes to ensure privacy"""
    while True:
        try:
            logger.info("🧹 Privacy Sweep: Cleaning up old files...")
            cutoff = time.time() - (30 * 60) # 30 minutes
            
            # Clean outputs
            for filename in os.listdir(OUTPUT_FOLDER):
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff:
                        try:
                            os.remove(filepath)
                            logger.info(f"Deleted old file: {filename}")
                        except Exception:
                            pass
            
            # Clean uploads (if any persisted, though usually tempfile handles this)
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff:
                        try:
                            os.remove(filepath)
                            logger.info(f"Deleted old upload: {filename}")
                        except Exception:
                            pass

        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
        
        time.sleep(900) # Run every 15 minutes

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
cleanup_thread.start()

# Initialize conversion engine
engine = ConversionEngine(
    output_dir=OUTPUT_FOLDER,
    enable_quality_gates=True
)

# Quota store
QUOTA_FILE = os.path.join(os.path.dirname(__file__), "quota_store.json")
DAILY_QUOTA_BYTES = int(os.getenv("DAILY_QUOTA_BYTES", str(200 * 1024 * 1024)))

def _load_quota():
    try:
        if os.path.exists(QUOTA_FILE):
            with open(QUOTA_FILE, "r") as f:
                return json.load(f)
    except Exception:
        logger.exception("Failed to load quota file")
    return {}

def _save_quota(store):
    try:
        with open(QUOTA_FILE, "w") as f:
            json.dump(store, f)
    except Exception:
        logger.exception("Failed to save quota file")

def check_and_increment_quota(client_ip, size_bytes):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    store = _load_quota()
    day = store.get(today, {})
    used = day.get(client_ip, 0)
    if used + size_bytes > DAILY_QUOTA_BYTES:
        return False, used
    day[client_ip] = used + size_bytes
    store[today] = day
    _save_quota(store)
    return True, day[client_ip]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_async_result(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@app.route("/api/convert", methods=["POST"])
@limiter.limit("60 per hour")
def convert_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        output_format = request.form.get("outputFormat")
        if not output_format:
            return jsonify({"error": "Output format required"}), 400
        client_ip = request.remote_addr or get_remote_address()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            size = os.path.getsize(tmp.name)
            allowed, used = check_and_increment_quota(client_ip, size)
            if not allowed:
                os.remove(tmp.name)
                return jsonify({"error": "Daily quota exceeded"}), 429
            try:
                params_raw = request.form.get("parameters") or "{}"
                try:
                    params = json.loads(params_raw) if isinstance(params_raw, str) else params_raw
                except Exception:
                    params = {}
                result = get_async_result(engine.convert(tmp.name, output_format, {"userId": request.form.get("userId", "anonymous"), "parameters": params}))
                return jsonify(result)
            except Exception:
                logger.exception("Conversion failed")
                return jsonify({"error": "Conversion failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in convert_file")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/image", methods=["POST"])
@limiter.limit("60 per hour")
def convert_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            format_str = request.form.get("format", "jpeg")
            quality = int(request.form.get("quality", 80))
            
            # Generate unique output filename
            timestamp = int(datetime.now().timestamp())
            original_name = Path(secure_filename(file.filename)).stem
            output_filename = f"{original_name}_{timestamp}.{format_str}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Perform conversion FIRST
            result = ImageConverter.convert(tmp.name, output_path, format_str, quality=quality)
            
            # Try to create recipe (don't fail if this errors)
            try:
                input_format = Path(file.filename).suffix[1:].lower()
                recipe = RecipeManager.create_recipe(
                    input_file=tmp.name,
                    output_file=output_path,
                    input_format=input_format,
                    output_format=format_str,
                    parameters={"quality": quality}
                )
                recipe = RecipeManager.finalize_recipe(recipe, output_path)
                result["recipe"] = recipe
            except Exception as e:
                logger.warning(f"Recipe generation failed: {e}")
                result["recipe"] = None
            
            # Add filename to result
            result["outputFileName"] = output_filename
            
            return jsonify(result)
        except Exception:
            logger.exception("Image conversion failed")
            return jsonify({"error": "Image conversion failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in convert_image")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/document/excel-to-csv", methods=["POST"])
@limiter.limit("60 per hour")
def excel_to_csv():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            
            # Unique filename
            timestamp = int(datetime.now().timestamp())
            base = Path(secure_filename(file.filename)).stem
            output_filename = f"{base}_{timestamp}.csv"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Convert
            result = DocumentConverter.excel_to_csv(tmp.name, output_path, sheet_index=int(request.form.get("sheetIndex", 0)))
            
            # Recipe
            try:
                recipe = RecipeManager.create_recipe(
                    input_file=tmp.name,
                    output_file=output_path,
                    input_format="xlsx",
                    output_format="csv"
                )
                recipe = RecipeManager.finalize_recipe(recipe, output_path)
                result["recipe"] = recipe
            except Exception as e:
                logger.warning(f"Recipe failed: {e}")
                result["recipe"] = None
                
            result["outputFileName"] = output_filename
            return jsonify(result)
        except Exception:
            logger.exception("excel_to_csv failed")
            return jsonify({"error": "Excel to CSV conversion failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in excel_to_csv")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/document/csv-to-excel", methods=["POST"])
@limiter.limit("60 per hour")
def csv_to_excel():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            
            # Unique filename
            timestamp = int(datetime.now().timestamp())
            base = Path(secure_filename(file.filename)).stem
            output_filename = f"{base}_{timestamp}.xlsx"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Convert
            result = DocumentConverter.csv_to_excel(tmp.name, output_path, sheet_name=request.form.get("sheetName", "Sheet1"))
            
            # Recipe
            try:
                recipe = RecipeManager.create_recipe(
                    input_file=tmp.name,
                    output_file=output_path,
                    input_format="csv",
                    output_format="xlsx"
                )
                recipe = RecipeManager.finalize_recipe(recipe, output_path)
                result["recipe"] = recipe
            except Exception as e:
                logger.warning(f"Recipe failed: {e}")
                result["recipe"] = None
                
            result["outputFileName"] = output_filename
            return jsonify(result)
        except Exception:
            logger.exception("csv_to_excel failed")
            return jsonify({"error": "CSV to Excel conversion failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in csv_to_excel")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/document/csv-to-parquet", methods=["POST"])
@limiter.limit("60 per hour")
def csv_to_parquet():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            
            # Unique filename
            timestamp = int(datetime.now().timestamp())
            base = Path(secure_filename(file.filename)).stem
            output_filename = f"{base}_{timestamp}.parquet"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Convert
            result = DocumentConverter.csv_to_parquet(tmp.name, output_path)
            
            # Recipe
            try:
                recipe = RecipeManager.create_recipe(
                    input_file=tmp.name,
                    output_file=output_path,
                    input_format="csv",
                    output_format="parquet"
                )
                recipe = RecipeManager.finalize_recipe(recipe, output_path)
                result["recipe"] = recipe
            except Exception as e:
                logger.warning(f"Recipe failed: {e}")
                result["recipe"] = None
                
            result["outputFileName"] = output_filename
            return jsonify(result)
        except Exception:
            logger.exception("csv_to_parquet failed")
            return jsonify({"error": "CSV to Parquet conversion failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in csv_to_parquet")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/image-metadata", methods=["POST"])
@limiter.limit("60 per hour")
def image_metadata():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            result = ImageConverter.get_metadata(tmp.name)
            return jsonify(result)
        except Exception:
            logger.exception("image_metadata failed")
            return jsonify({"error": "Metadata extraction failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in image_metadata")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversions/csv-validate", methods=["POST"])
@limiter.limit("60 per hour")
def csv_validate():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_" + secure_filename(file.filename))
        try:
            file.save(tmp.name)
            tmp.flush()
            required_columns = request.form.get("requiredColumns", "[]")
            required_columns = json.loads(required_columns)
            result = DocumentConverter.validate_csv(tmp.name, required_columns)
            return jsonify(result)
        except Exception:
            logger.exception("csv_validate failed")
            return jsonify({"error": "CSV validation failed"}), 500
        finally:
            try:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            except Exception:
                logger.exception("Failed to cleanup temp file")
    except Exception:
        logger.exception("Unhandled exception in csv_validate")
        return jsonify({"error": "Internal server error"}), 500

# ============================================================
# PDF CONVERSION ENDPOINTS
# ============================================================

@app.route("/api/conversions/pdf/to-word", methods=["POST"])
@limiter.limit("10 per hour")
def pdf_to_word():
    """Convert PDF to Word (DOCX)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.docx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Convert
        result = PDFConverter.pdf_to_word(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="pdf",
                output_format="docx"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")
        
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "pages": result.get("pages", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("PDF to Word conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/pdf/to-excel", methods=["POST"])
@limiter.limit("10 per hour")
def pdf_to_excel():
    """Convert PDF to Excel (XLSX)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.xlsx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = PDFConverter.pdf_to_excel(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="pdf",
                output_format="xlsx"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "tables": result.get("tables", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("PDF to Excel conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/word/to-pdf", methods=["POST"])
@limiter.limit("10 per hour")
def word_to_pdf():
    """Convert Word (DOCX) to PDF"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = PDFConverter.word_to_pdf(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="docx",
                output_format="pdf"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "paragraphs": result.get("paragraphs", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("Word to PDF conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/excel/to-pdf", methods=["POST"])
@limiter.limit("10 per hour")
def excel_to_pdf():
    """Convert Excel (XLSX) to PDF"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = PDFConverter.excel_to_pdf(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="xlsx",
                output_format="pdf"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "rows": result.get("rows", 0),
            "columns": result.get("columns", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("Excel to PDF conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/image/to-pdf", methods=["POST"])
@limiter.limit("20 per hour")
def image_to_pdf():
    """Convert Image to PDF"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Convert single image to PDF (images_to_pdf expects a list)
        result = PDFConverter.images_to_pdf([input_path], output_path)
        
        # Recipe
        recipe = None
        try:
            input_format = Path(filename).suffix[1:].lower()
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format=input_format,
                output_format="pdf"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "images": result.get("images", 1),
            "message": result.get("message", "Image converted to PDF")
        })
    
    except Exception as e:
        logger.exception("Image to PDF conversion failed")
        return jsonify({"error": str(e)}), 500

# ============================================================
# JSON CONVERSION ENDPOINTS
# ============================================================

@app.route("/api/conversions/csv/to-json", methods=["POST"])
@limiter.limit("20 per hour")
def csv_to_json():
    """Convert CSV to JSON"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.json"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = DocumentConverter.csv_to_json(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="csv",
                output_format="json"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "rows": result.get("rows", 0),
            "columns": result.get("columns", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("CSV to JSON conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/json/to-csv", methods=["POST"])
@limiter.limit("20 per hour")
def json_to_csv():
    """Convert JSON to CSV"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_{int(datetime.now().timestamp())}.csv"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = DocumentConverter.json_to_csv(input_path, output_path)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="json",
                output_format="csv"
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "rows": result.get("rows", 0),
            "columns": result.get("columns", 0),
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("JSON to CSV conversion failed")
        return jsonify({"error": str(e)}), 500

# ============================================================
# AUDIO CONVERSION ENDPOINTS
# ============================================================

@app.route("/api/conversions/audio", methods=["POST"])
@limiter.limit("20 per hour")
def convert_audio():
    """Convert audio files"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        # Get parameters
        format_str = request.form.get("format", "mp3")
        bitrate = request.form.get("bitrate", "192k")
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Unique output filename
        timestamp = int(datetime.now().timestamp())
        output_filename = f"{Path(filename).stem}_{timestamp}.{format_str}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = AudioConverter.convert(input_path, output_path, format_str, bitrate)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format=Path(filename).suffix[1:].lower(),
                output_format=format_str,
                parameters={"bitrate": bitrate}
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("Audio conversion failed")
        return jsonify({"error": str(e)}), 500

# ============================================================
# ARCHIVE CONVERSION ENDPOINTS
# ============================================================

@app.route("/api/conversions/archive", methods=["POST"])
@limiter.limit("20 per hour")
def convert_archive():
    """Convert/Create archives"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        # Get parameters
        format_str = request.form.get("format", "zip")
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Unique output filename
        timestamp = int(datetime.now().timestamp())
        output_filename = f"{Path(filename).stem}_{timestamp}.{format_str}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = ArchiveConverter.convert(input_path, output_path, format_str)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format=Path(filename).suffix[1:].lower(),
                output_format=format_str
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": os.path.getsize(output_path)},
            "message": result.get("message")
        })
    
    except Exception as e:
        logger.exception("Archive conversion failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversions/supported-formats", methods=["GET"])
def supported_formats():
    return jsonify({
        "images": ["jpeg", "jpg", "png", "webp", "gif", "bmp", "tiff", "svg", "heic"],
        "documents": ["csv", "xlsx", "parquet", "json", "pdf", "docx", "doc", "pptx", "ppt"],
        "documentInput": ["xlsx", "csv", "parquet", "json", "pdf", "docx"],
        "audio": ["mp3", "wav", "aac", "ogg", "m4a"]
    })

# ============================================================
# FILE SIZE REDUCTION ENDPOINTS
# ============================================================

@app.route("/api/compress/image", methods=["POST"])
@limiter.limit("20 per hour")
def compress_image():
    """Compress/reduce image file size"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        # Get compression parameters
        quality = int(request.form.get("quality", 85))
        max_dimension = request.form.get("maxDimension")
        max_dimension = int(max_dimension) if max_dimension else None
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Unique output filename
        stem = Path(filename).stem
        extension = Path(filename).suffix
        timestamp = int(datetime.now().timestamp())
        output_filename = f"{stem}_compressed_{timestamp}{extension}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = FileSizeReducer.compress_image(input_path, output_path, quality, max_dimension)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format=extension[1:].lower(),
                output_format=extension[1:].lower(),
                parameters={"quality": quality, "max_dimension": max_dimension}
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": result["compressedSize"]},
            "originalSize": result["originalSize"],
            "compressedSize": result["compressedSize"],
            "reductionPercent": result["reductionPercent"],
            "message": result["message"]
        })
    
    except Exception as e:
        logger.exception("Image compression failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/compress/pdf", methods=["POST"])
@limiter.limit("10 per hour")
def compress_pdf():
    """Compress/reduce PDF file size"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        compression_level = request.form.get("level", "medium")
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Unique output filename
        timestamp = int(datetime.now().timestamp())
        output_filename = f"{Path(filename).stem}_compressed_{timestamp}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = FileSizeReducer.compress_pdf(input_path, output_path, compression_level)
        
        # Recipe
        recipe = None
        try:
            recipe = RecipeManager.create_recipe(
                input_file=input_path,
                output_file=output_path,
                input_format="pdf",
                output_format="pdf",
                parameters={"level": compression_level}
            )
            recipe = RecipeManager.finalize_recipe(recipe, output_path)
        except Exception as e:
            logger.warning(f"Recipe failed: {e}")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            "success": True,
            "outputFileName": output_filename,
            "recipe": recipe,
            "output": {"file": output_filename, "size": result["compressedSize"]},
            "originalSize": result["originalSize"],
            "compressedSize": result["compressedSize"],
            "reductionPercent": result["reductionPercent"],
            "pages": result["pages"],
            "message": result["message"]
        })
    
    except Exception as e:
        logger.exception("PDF compression failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/compress/excel", methods=["POST"])
@limiter.limit("20 per hour")
def compress_excel():
    """Compress/reduce Excel file size"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_compressed.xlsx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = FileSizeReducer.compress_excel(input_path, output_path)
        os.remove(input_path)
        
        return jsonify({
            "success": True,
            "output": {"file": output_filename, "size": result["compressedSize"]},
            "originalSize": result["originalSize"],
            "compressedSize": result["compressedSize"],
            "reductionPercent": result["reductionPercent"],
            "message": result["message"]
        })
    
    except Exception as e:
        logger.exception("Excel compression failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/compress/csv", methods=["POST"])
@limiter.limit("20 per hour")
def compress_csv():
    """Compress/reduce CSV file size"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        remove_duplicates = request.form.get("removeDuplicates", "false").lower() == "true"
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_filename = f"{Path(filename).stem}_compressed.csv"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        result = FileSizeReducer.compress_csv(input_path, output_path, remove_duplicates)
        os.remove(input_path)
        
        return jsonify({
            "success": True,
            "output": {"file": output_filename, "size": result["compressedSize"]},
            "originalSize": result["originalSize"],
            "compressedSize": result["compressedSize"],
            "reductionPercent": result["reductionPercent"],
            "message": result["message"]
        })
    
    except Exception as e:
        logger.exception("CSV compression failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    """Download converted file"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception:
        logger.exception("File download failed")
        return jsonify({"error": "Download failed"}), 500

@app.route("/api/recipe/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    try:
        recipe_path = os.path.join(OUTPUT_FOLDER, f"{recipe_id}.recipe.yaml")
        if not os.path.exists(recipe_path):
            return jsonify({"error": "Recipe not found"}), 404
        with open(recipe_path, "r") as f:
            content = f.read()
        return content, 200, {"Content-Type": "application/x-yaml"}
    except Exception:
        logger.exception("get_recipe failed")
        return jsonify({"error": "Failed to retrieve recipe"}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat(), "environment": os.getenv("ENVIRONMENT", "development")})

@app.route("/api/formats", methods=["GET"])
def formats():
    return jsonify({"documents": ["pdf", "docx", "xlsx", "csv", "parquet"], "images": ["jpg", "jpeg", "png", "webp", "gif", "bmp"], "video": ["mp4", "webm", "mov", "avi"], "audio": ["mp3", "wav", "aac", "flac"]})

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large (max 500MB)"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.route("/api/feedback", methods=["POST"])
@limiter.limit("2 per hour")
def submit_feedback():
    """Submit user feedback/bug report"""
    try:
        data = request.json
        if not data or not data.get("message"):
            return jsonify({"error": "Message is required"}), 400
            
        # Add metadata headers
        data["userAgent"] = request.headers.get("User-Agent")
        
        result = FeedbackManager.save_feedback(data)
        return jsonify(result)
        
    except Exception as e:
        logger.exception("Feedback submission failed")
        return jsonify({"error": "Failed to save feedback"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Startup banner
    print("=" * 60)
    print("🔄 Next-Gen File Converter API")
    print("=" * 60)
    print(f"Environment: {environment}")
    print(f"Server: http://localhost:{port}")
    print(f"Health Check: http://localhost:{port}/api/health")
    print(f"CORS Origins: {allowed_origins}")
    print(f"Daily Quota: {DAILY_QUOTA_BYTES / (1024*1024):.0f}MB per IP")
    print("=" * 60)
    
    debug_flag = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_flag, host="0.0.0.0", port=port)

