from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# ============================================
# ✅ Configuration
# ============================================
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_FILE_SIZE"] = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# ✅ Dangerous extensions - NEVER allow these!
DANGEROUS_EXTENSIONS = {'exe', 'sh', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js'}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ============================================
# Helper Functions
# ============================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    # ✅ Security: Block dangerous extensions
    if ext in DANGEROUS_EXTENSIONS:
        return False
    
    return ext in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """
    Generate unique filename to prevent conflicts
    Format: uuid_timestamp_originalname.ext
    Example: a1b2c3d4_20241107_image.jpg
    """
    # Get extension
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # Get name without extension
    name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
    
    # Make it safe
    safe_name = secure_filename(name)
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine
    unique_filename = f"{unique_id}_{timestamp}_{safe_name}.{ext}"
    
    return unique_filename

def get_file_size_mb(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    return round(size_bytes / (1024 * 1024), 2)

# ============================================
# 1️⃣ Upload File (SECURE)
# ============================================
@app.route('/upload', methods=['POST'])
def upload():
    """
    Secure file upload with:
    - File size check BEFORE upload
    - Unique filename generation
    - Dangerous extension blocking
    """
    
    # Check if file exists
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # ✅ Security: Check file size BEFORE saving
    file.seek(0, os.SEEK_END)  # Move to end of file
    file_size = file.tell()  # Get size
    file.seek(0)  # Move back to start
    
    if file_size > app.config["MAX_FILE_SIZE"]:
        max_mb = app.config["MAX_FILE_SIZE"] / (1024 * 1024)
        return jsonify({
            "error": f"File too large! Maximum {max_mb}MB allowed"
        }), 413
    
    # Check file type
    if not allowed_file(file.filename):
        return jsonify({
            "error": "File type not allowed",
            "allowed_types": list(ALLOWED_EXTENSIONS)
        }), 400
    
    # ✅ Security: Generate UNIQUE filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Save file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(filepath)
    
    # Get file info
    file_size_mb = get_file_size_mb(filepath)
    
    return jsonify({
        "message": "✅ File uploaded successfully",
        "original_name": file.filename,
        "saved_as": unique_filename,
        "size_mb": file_size_mb,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "download_url": f"/download/{unique_filename}"
    }), 200


# ============================================
# 2️⃣ Download File (SECURE)
# ============================================
@app.route('/download/<filename>')
def download(filename):
    """
    Secure download with:
    - Path traversal protection
    - File existence check
    """
    
    # ✅ Security: Prevent path traversal attacks
    # Example: /download/../../etc/passwd → blocked!
    filename = secure_filename(filename)
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    # ✅ Security: Check if file is actually in uploads folder
    # This prevents: /download/etc_passwd
    real_path = os.path.realpath(filepath)
    upload_folder_real = os.path.realpath(app.config["UPLOAD_FOLDER"])
    
    if not real_path.startswith(upload_folder_real):
        return jsonify({"error": "Access denied"}), 403
    
    # Check if file exists
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(filepath, as_attachment=True)


# ============================================
# 3️⃣ List Files (SECURE)
# ============================================
@app.route('/files')
def files():
    """
    List files with detailed info
    """
    
    try:
        all_files = os.listdir(app.config["UPLOAD_FOLDER"])
    except Exception as e:
        return jsonify({"error": "Cannot read files"}), 500
    
    files_list = []
    total_size_mb = 0
    
    for filename in all_files:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        # Skip if not a file
        if not os.path.isfile(filepath):
            continue
        
        file_size = os.path.getsize(filepath)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        total_size_mb += file_size_mb
        
        # Get upload date from file modification time
        upload_time = os.path.getmtime(filepath)
        upload_date = datetime.fromtimestamp(upload_time).strftime("%Y-%m-%d %H:%M:%S")
        
        files_list.append({
            "filename": filename,
            "size_mb": file_size_mb,
            "uploaded": upload_date,
            "download_url": f"/download/{filename}"
        })
    
    return jsonify({
        "total_files": len(files_list),
        "total_size_mb": round(total_size_mb, 2),
        "files": files_list
    })


# ============================================
# 4️⃣ Delete File (SECURE)
# ============================================
@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    """
    Secure delete with path traversal protection
    
    ⚠️ Note: In production, you should add authentication!
    Only file owner or admin should be able to delete.
    """
    
    # ✅ Security: Prevent path traversal
    filename = secure_filename(filename)
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    # ✅ Security: Check if file is in uploads folder
    real_path = os.path.realpath(filepath)
    upload_folder_real = os.path.realpath(app.config["UPLOAD_FOLDER"])
    
    if not real_path.startswith(upload_folder_real):
        return jsonify({"error": "Access denied"}), 403
    
    # Check if file exists
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    # Delete file
    try:
        os.remove(filepath)
        return jsonify({
            "message": "✅ File deleted successfully",
            "filename": filename
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to delete file"}), 500


# ============================================
# 5️⃣ System Info (For Testing)
# ============================================
@app.route('/info')
def info():
    """API information and statistics"""
    
    total_files = len([f for f in os.listdir(app.config["UPLOAD_FOLDER"]) 
                       if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f))])
    
    return jsonify({
        "api_name": "Secure File Upload API",
        "version": "2.0",
        "security_features": [
            "Unique filename generation",
            "Path traversal protection",
            "Dangerous extension blocking",
            "File size check before upload",
            "Secure filename sanitization"
        ],
        "config": {
            "upload_folder": app.config["UPLOAD_FOLDER"],
            "max_file_size_mb": app.config["MAX_FILE_SIZE"] / (1024 * 1024),
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "blocked_extensions": list(DANGEROUS_EXTENSIONS)
        },
        "statistics": {
            "total_files": total_files
        },
        "endpoints": {
            "upload": "POST /upload",
            "download": "GET /download/<filename>",
            "list": "GET /files",
            "delete": "DELETE /delete/<filename>",
            "info": "GET /info"
        }
    })


# ============================================
# Error Handlers
# ============================================
@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded"""
    max_mb = app.config["MAX_FILE_SIZE"] / (1024 * 1024)
    return jsonify({
        "error": f"File too large! Maximum {max_mb}MB allowed"
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({"error": "Internal server error"}), 500


# ============================================
# Run
# ============================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🔒 SECURE File Upload API")
    print("=" * 60)
    print("\n✅ Security Features:")
    print("   - Unique filename (prevents overwrite)")
    print("   - Path traversal protection")
    print("   - Dangerous extension blocking")
    print("   - File size check BEFORE upload")
    print("   - Secure filename sanitization")
    print("\n⚙️  Configuration:")
    print(f"   - Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"   - Max file size: {app.config['MAX_FILE_SIZE'] / (1024*1024)}MB")
    print(f"   - Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"   - Blocked: {', '.join(DANGEROUS_EXTENSIONS)}")
    print("\n🌐 Running on: http://localhost:5000")
    print("📊 System info: http://localhost:5000/info")
    print("=" * 60)
    print()
    
    app.run(debug=True, port=5000)