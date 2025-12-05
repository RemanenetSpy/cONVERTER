"""
Flask Backend Server for File Converter
Handles file conversions, recipes, and API endpoints
"""

import os
import asyncio
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path

from core.conversion_engine import ConversionEngine
from core.recipe_manager import RecipeManager
from core.image_converter import ImageConverter
from core.document_converter import DocumentConverter
from core.quality_gate import QualityGate

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff",
    "csv", "xlsx", "xls", "parquet", "mp4", "avi", "mov", "mp3", "wav"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize conversion engine
engine = ConversionEngine(
    output_dir=OUTPUT_FOLDER,
    enable_quality_gates=True
)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_async_result(coro):
    """Helper to run async functions"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


# ==================== Main Conversion Routes ====================

@app.route("/api/convert", methods=["POST"])
def convert_file():
    """Convert a file and generate recipe"""
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
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        try:
            # Execute conversion
            result = get_async_result(
                engine.convert(
                    input_path,
                    output_format,
                    {
                        "userId": request.form.get("userId", "anonymous"),
                        "parameters": request.form.get("parameters", {})
                    }
                )
            )
            
            # Clean up uploaded file
            if os.path.exists(input_path):
                os.remove(input_path)
            
            return jsonify(result)
        
        except Exception as e:
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/image", methods=["POST"])
def convert_image():
    """Convert image format"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        format_str = request.form.get("format", "jpeg")
        quality = int(request.form.get("quality", 80))
        
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{Path(filename).stem}.{format_str}"
        )
        
        result = ImageConverter.convert(
            input_path,
            output_path,
            format_str,
            quality=quality
        )
        
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/document/excel-to-csv", methods=["POST"])
def excel_to_csv():
    """Convert Excel to CSV"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{Path(filename).stem}.csv"
        )
        
        result = DocumentConverter.excel_to_csv(
            input_path,
            output_path,
            sheet_index=int(request.form.get("sheetIndex", 0))
        )
        
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/document/csv-to-excel", methods=["POST"])
def csv_to_excel():
    """Convert CSV to Excel"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{Path(filename).stem}.xlsx"
        )
        
        result = DocumentConverter.csv_to_excel(
            input_path,
            output_path,
            sheet_name=request.form.get("sheetName", "Sheet1")
        )
        
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/document/csv-to-parquet", methods=["POST"])
def csv_to_parquet():
    """Convert CSV to Parquet"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{Path(filename).stem}.parquet"
        )
        
        result = DocumentConverter.csv_to_parquet(input_path, output_path)
        
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/image-metadata", methods=["POST"])
def image_metadata():
    """Get image metadata"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        result = ImageConverter.get_metadata(input_path)
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/csv-validate", methods=["POST"])
def csv_validate():
    """Validate CSV structure"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        required_columns = request.form.get("requiredColumns", "[]")
        import json
        required_columns = json.loads(required_columns)
        
        result = DocumentConverter.validate_csv(input_path, required_columns)
        os.remove(input_path)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversions/supported-formats", methods=["GET"])
def supported_formats():
    """Get supported formats"""
    return jsonify({
        "images": ["jpeg", "jpg", "png", "webp", "gif", "bmp", "tiff"],
        "documents": ["csv", "xlsx", "parquet"],
        "documentInput": ["xlsx", "csv", "parquet"],
        "video": ["mp4", "webm", "mov", "avi"],
        "audio": ["mp3", "wav", "aac", "flac"]
    })


# ==================== Recipe Routes ====================

@app.route("/api/recipe/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    """Retrieve a recipe"""
    try:
        recipe_path = os.path.join(OUTPUT_FOLDER, f"{recipe_id}.recipe.yaml")
        
        if not os.path.exists(recipe_path):
            return jsonify({"error": "Recipe not found"}), 404
        
        with open(recipe_path, "r") as f:
            content = f.read()
        
        return content, 200, {"Content-Type": "application/x-yaml"}
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Health & Status Routes ====================

@app.route("/api/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "version": "0.1.0",
        "timestamp": str(Path(__file__).stat().st_mtime)
    })


@app.route("/api/formats", methods=["GET"])
def formats():
    """Get all supported formats"""
    return jsonify({
        "documents": ["pdf", "docx", "xlsx", "csv", "parquet"],
        "images": ["jpg", "jpeg", "png", "webp", "gif", "bmp"],
        "video": ["mp4", "webm", "mov", "avi"],
        "audio": ["mp3", "wav", "aac", "flac"]
    })


# ==================== Error Handlers ====================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return jsonify({"error": "File too large (max 500MB)"}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"""
╔════════════════════════════════════════╗
║   File Converter API Server (Python)   ║
║   Running on http://localhost:{port}     ║
╚════════════════════════════════════════╝
    """)
    app.run(debug=True, port=port)
