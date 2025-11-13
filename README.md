📁 File Upload & Download API
Secure file upload/download system with Flask.

✨ Features
✅ Single & multiple file upload
✅ File type validation
✅ Size limit (configurable)
✅ Unique filename generation
✅ Download & preview
✅ File listing & deletion
✅ Path traversal protection
🚀 Quick Start
pip install flask werkzeug
python app.py
📡 API Endpoints
Upload:

POST /upload
Form-data: file = your_file.jpg
List Files:

GET /files
Download:

GET /download/filename.jpg
Delete:

DELETE /delete/filename.jpg
⚙️ Configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'pdf'}
💻 Tech Stack
Python Flask
Secure file handling
📫 Contact
fahad.integration.ml@gmail.com
