# 📁 File Upload & Download API

Secure file upload/download system with Flask.

## ✨ Features
- ✅ Single & multiple file upload
- ✅ File type validation
- ✅ Size limit (configurable)
- ✅ Unique filename generation
- ✅ Download & preview
- ✅ File listing & deletion
- ✅ Path traversal protection

## 🚀 Quick Start
```bash
pip install flask werkzeug
python app.py
```

## 📡 API Endpoints

**Upload:**
```bash
POST /upload
Form-data: file = your_file.jpg
```

**List Files:**
```bash
GET /files
```

**Download:**
```bash
GET /download/filename.jpg
```

**Delete:**
```bash
DELETE /delete/filename.jpg
```

## ⚙️ Configuration
```python
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'pdf'}
```

## 💻 Tech Stack
- Python Flask
- Secure file handling

## 📫 Contact
fahad.integration.ml@gmail.com
