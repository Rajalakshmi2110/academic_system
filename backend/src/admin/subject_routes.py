"""
Subject Management Routes - Admin API for managing subjects
"""
from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from subject_manager import SubjectManager

subject_bp = Blueprint('subjects', __name__)
subject_manager = SubjectManager()

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
    """Add new subject"""
    try:
        data = request.json
        subject_id = data.get('id', '').lower().replace(' ', '_')
        name = data.get('name', '')
        code = data.get('code', '')
        
        if not subject_id or not name:
            return jsonify({'error': 'Subject ID and name required'}), 400
        
        subject = subject_manager.add_subject(subject_id, name, code)
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

@subject_bp.route('/delete/<subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete (deactivate) subject"""
    try:
        subject = subject_manager.delete_subject(subject_id)
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
