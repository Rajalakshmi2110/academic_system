from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
from pathlib import Path
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = Path('/Users/rathrajy/learning/project/DS')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
ADMIN_PASSWORD = 'admin123'

# Create ClassNotes subfolder for new uploads
CLASS_NOTES_FOLDER = UPLOAD_FOLDER / 'ClassNotes'
CLASS_NOTES_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get('password', '')
    
    if password == ADMIN_PASSWORD:
        return jsonify({'status': 'success', 'message': 'Login successful'})
    return jsonify({'status': 'error', 'message': 'Invalid password'}), 401

@admin_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    folder = request.form.get('folder', '')  # Get folder name from form
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        
        # Create subfolder if specified
        if folder:
            folder_path = CLASS_NOTES_FOLDER / secure_filename(folder)
            folder_path.mkdir(parents=True, exist_ok=True)
            filepath = folder_path / filename
        else:
            filepath = CLASS_NOTES_FOLDER / filename
        
        file.save(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'File {filename} uploaded',
            'filename': filename,
            'folder': folder,
            'size': filepath.stat().st_size,
            'uploaded_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/list-pdfs', methods=['GET'])
def list_pdfs():
    try:
        folders = {}
        
        # Define folder categories
        categories = {
            'Textbook': UPLOAD_FOLDER / 'Textbook',
            'Syllabus': UPLOAD_FOLDER / 'Syllabus',
            'ClassNotes': UPLOAD_FOLDER / 'ClassNotes'
        }
        
        for category, base_path in categories.items():
            if not base_path.exists():
                continue
                
            # Scan recursively within each category
            for pdf_file in base_path.rglob('*.pdf'):
                stat = pdf_file.stat()
                relative_path = pdf_file.relative_to(UPLOAD_FOLDER)
                
                # Get folder path within category
                folder_parts = relative_path.parts[1:-1]  # Skip category and filename
                if folder_parts:
                    folder_name = f"{category}/{'/'.join(folder_parts)}"
                else:
                    folder_name = category
                
                if folder_name not in folders:
                    folders[folder_name] = []
                
                folders[folder_name].append({
                    'filename': pdf_file.name,
                    'path': str(relative_path),
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Also scan for JSON files in Syllabus
        syllabus_path = UPLOAD_FOLDER / 'Syllabus'
        if syllabus_path.exists():
            for json_file in syllabus_path.rglob('*.json'):
                stat = json_file.stat()
                relative_path = json_file.relative_to(UPLOAD_FOLDER)
                
                if 'Syllabus' not in folders:
                    folders['Syllabus'] = []
                
                folders['Syllabus'].append({
                    'filename': json_file.name,
                    'path': str(relative_path),
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort files within each folder
        for folder in folders:
            folders[folder].sort(key=lambda x: x['modified'], reverse=True)
        
        total = sum(len(files) for files in folders.values())
        return jsonify({'folders': folders, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/delete-pdf', methods=['DELETE'])
def delete_pdf():
    try:
        data = request.json
        filepath = data.get('path', '')
        
        if not filepath:
            return jsonify({'error': 'Path required'}), 400
        
        full_path = UPLOAD_FOLDER / filepath
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        full_path.unlink()
        return jsonify({'status': 'success', 'message': f'{filepath} deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rebuild-vector-db', methods=['POST'])
def rebuild_vector_db():
    try:
        script_path = Path(__file__).parent.parent.parent / 'scripts' / 'rebuild_vector_db.py'
        
        result = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Vector database rebuilt',
                'output': result.stdout
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Rebuild failed',
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        pdf_count = len(list(UPLOAD_FOLDER.rglob('*.pdf')))
        
        vector_db_path = Path(__file__).parent.parent.parent / 'data' / 'vector_db'
        chunks_file = vector_db_path / 'chunks.pkl'
        
        import pickle
        if chunks_file.exists():
            with open(chunks_file, 'rb') as f:
                chunks = pickle.load(f)
            chunk_count = len(chunks)
        else:
            chunk_count = 0
        
        return jsonify({
            'pdfs_uploaded': pdf_count,
            'vector_chunks': chunk_count,
            'upload_folder': str(UPLOAD_FOLDER)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
