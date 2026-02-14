from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
from pathlib import Path
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = Path('/Users/rathrajy/learning/project/DS/ClassNotes')
ALLOWED_EXTENSIONS = {'pdf'}
ADMIN_PASSWORD = 'admin123'

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

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
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'File {filename} uploaded',
            'filename': filename,
            'size': filepath.stat().st_size,
            'uploaded_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/list-pdfs', methods=['GET'])
def list_pdfs():
    try:
        pdfs = []
        for pdf_file in UPLOAD_FOLDER.glob('*.pdf'):
            stat = pdf_file.stat()
            pdfs.append({
                'filename': pdf_file.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        pdfs.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'pdfs': pdfs, 'total': len(pdfs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/delete-pdf/<filename>', methods=['DELETE'])
def delete_pdf(filename):
    try:
        filename = secure_filename(filename)
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        filepath.unlink()
        return jsonify({'status': 'success', 'message': f'{filename} deleted'})
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
        pdf_count = len(list(UPLOAD_FOLDER.glob('*.pdf')))
        
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
