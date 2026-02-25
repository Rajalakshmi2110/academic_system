"""
Subject Manager - Handles multi-subject operations
"""
import json
import os
from pathlib import Path
from datetime import datetime

class SubjectManager:
    def __init__(self, base_path=None):
        if base_path is None:
            # Default: subjects/ folder at project root
            backend_dir = Path(__file__).parent.parent.parent
            self.base_path = backend_dir / "subjects"
        else:
            self.base_path = Path(base_path)
        
        self.config_file = self.base_path / "subjects.json"
        self._ensure_config()
    
    def _ensure_config(self):
        if not self.config_file.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
            self._save_config({"subjects": []})
    
    def _load_config(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_all_subjects(self):
        config = self._load_config()
        return config.get('subjects', [])
    
    def get_active_subjects(self):
        return [s for s in self.get_all_subjects() if s.get('active', False)]
    
    def get_subject(self, subject_id):
        subjects = self.get_all_subjects()
        for subject in subjects:
            if subject['id'] == subject_id:
                return subject
        return None
    
    def add_subject(self, subject_id, name, code=""):
        config = self._load_config()
        
        if any(s['id'] == subject_id for s in config['subjects']):
            raise ValueError(f"Subject {subject_id} already exists")
        
        subject_path = self.base_path / subject_id
        (subject_path / "documents").mkdir(parents=True, exist_ok=True)
        (subject_path / "vector_db").mkdir(parents=True, exist_ok=True)
        (subject_path / "models").mkdir(parents=True, exist_ok=True)
        
        new_subject = {
            "id": subject_id,
            "name": name,
            "code": code,
            "active": False,
            "created_at": datetime.now().isoformat(),
            "document_count": 0,
            "model_trained": False
        }
        config['subjects'].append(new_subject)
        self._save_config(config)
        
        return new_subject
    
    def update_subject(self, subject_id, **kwargs):
        config = self._load_config()
        
        for subject in config['subjects']:
            if subject['id'] == subject_id:
                subject.update(kwargs)
                self._save_config(config)
                return subject
        
        raise ValueError(f"Subject {subject_id} not found")
    
    def delete_subject(self, subject_id, permanent=False):
        """Soft delete (active=False) or permanent delete (remove folder)"""
        if permanent:
            import shutil
            config = self._load_config()
            config['subjects'] = [s for s in config['subjects'] if s['id'] != subject_id]
            self._save_config(config)
            
            subject_path = self.base_path / subject_id
            if subject_path.exists():
                shutil.rmtree(subject_path)
            
            return {'id': subject_id, 'deleted': True}
        else:
            return self.update_subject(subject_id, active=False)
    
    def get_subject_path(self, subject_id, subdir=""):
        path = self.base_path / subject_id
        if subdir:
            path = path / subdir
        return str(path)
    
    def get_documents_path(self, subject_id):
        return Path(self.base_path) / subject_id / "documents"
    
    def get_vector_db_path(self, subject_id):
        return Path(self.base_path) / subject_id / "vector_db"
    
    def get_model_path(self, subject_id):
        return Path(self.base_path) / subject_id / "models" / "layer1_distilbert"
    
    def get_syllabus_path(self, subject_id):
        return Path(self.base_path) / subject_id / "syllabus.json"
