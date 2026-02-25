"""
Subject Management Routes - Admin API for managing subjects
"""
from flask import Blueprint, request, jsonify
import sys
import json
import threading
from pathlib import Path
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from subject_manager import SubjectManager

# Import training pipeline from scripts
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))
from training_pipeline import TrainingPipeline

subject_bp = Blueprint('subjects', __name__)
subject_manager = SubjectManager()
training_pipeline = TrainingPipeline()

@subject_bp.route('/list', methods=['GET'])
def list_subjects():
    """Get all subjects"""
    try:
        subjects = subject_manager.get_all_subjects()
        return jsonify({'subjects': subjects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/active', methods=['GET'])
def list_active_subjects():
    """Get only active subjects (for student dropdown)"""
    try:
        subjects = subject_manager.get_active_subjects()
        return jsonify({'subjects': subjects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/add', methods=['POST'])
def add_subject():
    """Add new subject with files (syllabus + documents)"""
    try:
        # Get form data
        name = request.form.get('name', '')
        code = request.form.get('code', '')
        subject_id = request.form.get('id', '').lower().replace(' ', '_')
        auto_train = request.form.get('auto_train', 'true') == 'true'
        
        if not subject_id or not name:
            return jsonify({'error': 'Subject ID and name required'}), 400
        
        # Create subject folder structure
        subject = subject_manager.add_subject(subject_id, name, code)
        
        # Handle syllabus file
        syllabus_file = request.files.get('syllabus')
        if syllabus_file:
            syllabus_path = subject_manager.get_syllabus_path(subject_id)
            syllabus_content = json.load(syllabus_file)
            with open(syllabus_path, 'w') as f:
                json.dump(syllabus_content, f, indent=2)
        
        # Handle document files
        document_files = request.files.getlist('documents')
        docs_path = subject_manager.get_documents_path(subject_id)
        
        for doc_file in document_files:
            if doc_file.filename:
                filename = secure_filename(doc_file.filename)
                doc_file.save(docs_path / filename)
        
        # Update document count
        doc_count = len(list(docs_path.rglob('*.pdf')))
        subject_manager.update_subject(subject_id, document_count=doc_count)
        
        # Start training pipeline in background if requested
        if auto_train and syllabus_file:
            def train_async():
                try:
                    print(f"\n[TRAINING] Starting background training for {subject_id}")
                    training_pipeline.run_full_pipeline(subject_id)
                    print(f"[TRAINING] ✓ Completed for {subject_id}")
                except Exception as e:
                    import traceback
                    error_msg = f"[TRAINING] ✗ Failed for {subject_id}: {str(e)}\n{traceback.format_exc()}"
                    print(error_msg)
                    # Log to file
                    import datetime
                    log_file = Path(__file__).parent.parent.parent / 'training_errors.log'
                    with open(log_file, 'a') as f:
                        f.write(f"\n{'='*60}\n")
                        f.write(f"{datetime.datetime.now().isoformat()}\n")
                        f.write(error_msg)
                        f.write(f"\n{'='*60}\n")
            
            thread = threading.Thread(target=train_async)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'status': 'success',
                'subject': subject,
                'message': 'Subject created. Training started in background.'
            })
        
        return jsonify({'status': 'success', 'subject': subject})
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/update/<subject_id>', methods=['PUT'])
def update_subject(subject_id):
    """Update subject properties"""
    try:
        data = request.json
        subject = subject_manager.update_subject(subject_id, **data)
        return jsonify({'status': 'success', 'subject': subject})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/train/<subject_id>', methods=['POST'])
def train_subject(subject_id):
    """Manually trigger training for a subject"""
    try:
        import threading
        
        subject = subject_manager.get_subject(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if syllabus exists
        syllabus_path = subject_manager.get_syllabus_path(subject_id)
        if not syllabus_path.exists():
            return jsonify({'error': 'Syllabus not found. Upload syllabus first.'}), 400
        
        def train_async():
            try:
                print(f"\n[TRAINING] Starting manual training for {subject_id}")
                training_pipeline.run_full_pipeline(subject_id)
                print(f"[TRAINING] ✓ Completed for {subject_id}")
            except Exception as e:
                import traceback
                error_msg = f"[TRAINING] ✗ Failed for {subject_id}: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                import datetime
                log_file = Path(__file__).parent.parent.parent / 'training_errors.log'
                with open(log_file, 'a') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"{datetime.datetime.now().isoformat()}\n")
                    f.write(error_msg)
                    f.write(f"\n{'='*60}\n")
        
        thread = threading.Thread(target=train_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Training started in background (4-6 minutes)'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/delete/<subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete subject permanently"""
    try:
        permanent = request.args.get('permanent', 'true').lower() == 'true'
        subject = subject_manager.delete_subject(subject_id, permanent=permanent)
        return jsonify({'status': 'success', 'subject': subject})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/<subject_id>', methods=['GET'])
def get_subject(subject_id):
    """Get specific subject details"""
    try:
        subject = subject_manager.get_subject(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        return jsonify({'subject': subject})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
