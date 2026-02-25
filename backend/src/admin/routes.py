from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from subject_manager import SubjectManager

admin_bp = Blueprint('admin', __name__)
subject_manager = SubjectManager()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'json'}
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

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
    subject_id = request.form.get('subject_id', 'data_structures')  # Default to DS
    folder = request.form.get('folder', '')  # Optional subfolder
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        # Get subject's documents folder
        docs_path = Path(subject_manager.get_documents_path(subject_id))
        docs_path.mkdir(parents=True, exist_ok=True)
        
        filename = secure_filename(file.filename)
        
        # Create subfolder if specified
        if folder:
            folder_path = docs_path / secure_filename(folder)
            folder_path.mkdir(parents=True, exist_ok=True)
            filepath = folder_path / filename
        else:
            filepath = docs_path / filename
        
        file.save(filepath)
        
        # Update document count
        subject = subject_manager.get_subject(subject_id)
        if subject:
            doc_count = subject.get('document_count', 0) + 1
            subject_manager.update_subject(subject_id, document_count=doc_count)
        
        return jsonify({
            'status': 'success',
            'message': f'File {filename} uploaded',
            'filename': filename,
            'subject_id': subject_id,
            'folder': folder,
            'size': filepath.stat().st_size,
            'uploaded_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/list-pdfs', methods=['GET'])
def list_pdfs():
    try:
        subject_id = request.args.get('subject_id', 'data_structures')
        
        # Get subject's documents folder
        docs_path = Path(subject_manager.get_documents_path(subject_id))
        
        folders = {}
        
        if docs_path.exists():
            # Scan recursively for all supported files
            for file_path in docs_path.rglob('*'):
                if file_path.suffix.lower() not in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.json']:
                    continue
                    
                stat = file_path.stat()
                relative_path = file_path.relative_to(docs_path)
                
                # Get folder path
                folder_parts = relative_path.parts[:-1]
                if folder_parts:
                    folder_name = '/'.join(folder_parts)
                else:
                    folder_name = 'Root'
                
                if folder_name not in folders:
                    folders[folder_name] = []
                
                folders[folder_name].append({
                    'filename': file_path.name,
                    'path': str(relative_path),
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort files within each folder
        for folder in folders:
            folders[folder].sort(key=lambda x: x['modified'], reverse=True)
        
        total = sum(len(files) for files in folders.values())
        return jsonify({'folders': folders, 'total': total, 'subject_id': subject_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/delete-pdf', methods=['DELETE'])
def delete_pdf():
    try:
        data = request.json
        filepath = data.get('path', '')
        subject_id = data.get('subject_id', 'data_structures')
        
        if not filepath:
            return jsonify({'error': 'Path required'}), 400
        
        docs_path = Path(subject_manager.get_documents_path(subject_id))
        full_path = docs_path / filepath
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        full_path.unlink()
        
        # Update document count
        subject = subject_manager.get_subject(subject_id)
        if subject:
            doc_count = max(0, subject.get('document_count', 1) - 1)
            subject_manager.update_subject(subject_id, document_count=doc_count)
        
        return jsonify({'status': 'success', 'message': f'{filepath} deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rebuild-vector-db', methods=['POST'])
def rebuild_vector_db():
    try:
        data = request.json or {}
        subject_id = data.get('subject_id', 'data_structures')
        
        # Use build_vector_db.py (same as rebuild)
        script_path = Path(__file__).parent.parent.parent / 'scripts' / 'build_vector_db.py'
        docs_path = subject_manager.get_documents_path(subject_id)
        vector_db_path = subject_manager.get_vector_db_path(subject_id)
        
        result = subprocess.run(
            [sys.executable, str(script_path), str(docs_path), str(vector_db_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': f'Vector database rebuilt for {subject_id}',
                'output': result.stdout,
                'subject_id': subject_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Rebuild failed',
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/download-file', methods=['POST'])
def download_file():
    try:
        data = request.json
        filepath = data.get('path', '')
        subject_id = data.get('subject_id', 'data_structures')
        
        if not filepath:
            return jsonify({'error': 'Path required'}), 400
        
        docs_path = Path(subject_manager.get_documents_path(subject_id))
        full_path = docs_path / filepath
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(full_path, as_attachment=True, download_name=full_path.name)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        subject_id = request.args.get('subject_id', 'data_structures')
        
        # Count files in subject's documents folder
        docs_path = Path(subject_manager.get_documents_path(subject_id))
        file_count = 0
        if docs_path.exists():
            file_count = (
                len(list(docs_path.rglob('*.pdf'))) +
                len(list(docs_path.rglob('*.doc'))) +
                len(list(docs_path.rglob('*.docx'))) +
                len(list(docs_path.rglob('*.ppt'))) +
                len(list(docs_path.rglob('*.pptx')))
            )
        
        # Count chunks in subject's vector DB
        vector_db_path = Path(subject_manager.get_vector_db_path(subject_id))
        chunks_file = vector_db_path / 'chunks.pkl'
        
        import pickle
        if chunks_file.exists():
            with open(chunks_file, 'rb') as f:
                chunks = pickle.load(f)
            chunk_count = len(chunks)
        else:
            chunk_count = 0
        
        return jsonify({
            'pdfs_uploaded': file_count,
            'vector_chunks': chunk_count,
            'subject_id': subject_id,
            'upload_folder': str(docs_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
