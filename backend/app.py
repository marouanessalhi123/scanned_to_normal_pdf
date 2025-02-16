import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from pathlib import Path
import subprocess
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
CORS(app, resources={r"/*": {"origins": "https://frontend-brown-ten-56.vercel.app/"}})


# Configuration
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXTENSIONS = {"pdf"}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    return text

def run_ocrmypdf(input_pdf):
    """Runs OCR on a PDF and extracts text"""
    input_path = Path(input_pdf)
    output_path = Path(PROCESSED_FOLDER) / f"{input_path.stem}_ocr{input_path.suffix}"

    command = ["ocrmypdf", "--force-ocr", str(input_path), str(output_path)]
    
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if process.returncode != 0:
            print(f"OCR Error: {process.stderr}")
            return None, None

        extracted_text = extract_text_from_pdf(str(output_path))
        return str(output_path), extracted_text

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None, None

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handle PDF upload and OCR processing"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF files are allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        output_file, extracted_text = run_ocrmypdf(file_path)
        if output_file is None or extracted_text is None:
            return jsonify({"error": "OCR processing failed"}), 500

        return jsonify({
            "message": "File processed successfully",
            "file_url": f"/download/{Path(output_file).name}",
            "text": extracted_text
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/download/<filename>", methods=["GET"])
def download_pdf(filename):
    """Handle download of processed PDFs"""
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route("/test", methods=["GET"])
def test_connection():
    return jsonify({"message": "Connection successful!"}), 200

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    """Serves the React application"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)