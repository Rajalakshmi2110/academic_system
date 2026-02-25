"""
Automated training pipeline for new subjects
Handles: data generation -> model training -> vector DB creation
"""
import json
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from subject_manager import SubjectManager

class TrainingPipeline:
    def __init__(self):
        self.subject_manager = SubjectManager()
        self.backend_root = Path(__file__).parent.parent
        self.scripts_dir = self.backend_root / 'scripts'
        
    def generate_training_data(self, subject_id, target_count=1800):
        syllabus_path = self.subject_manager.get_syllabus_path(subject_id)
        output_path = self.subject_manager.get_documents_path(subject_id) / 'training_data.json'
        
        print(f"[1/3] Generating {target_count} training samples...")
        
        # Run generation script
        script_path = self.scripts_dir / 'generate_training_data.py'
        result = subprocess.run([
            sys.executable, str(script_path),
            str(syllabus_path), str(output_path), str(target_count)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Data generation failed: {result.stderr}")
        
        print(f"✓ Training data saved to {output_path}")
        return output_path
    
    def train_layer1_model(self, subject_id, training_data_path):
        model_output_path = self.subject_manager.get_model_path(subject_id)
        
        print(f"[2/3] Training Layer 1 model...")
        
        script_path = self.backend_root / 'src' / 'layer1_classifier' / 'train_script.py'
        result = subprocess.run([
            sys.executable, str(script_path),
            str(training_data_path), str(model_output_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Model training failed: {result.stderr}")
        
        print(f"✓ Model saved to {model_output_path}")
        return model_output_path
    
    def build_vector_db(self, subject_id):
        print(f"[3/3] Building vector database...")
        
        docs_path = self.subject_manager.get_documents_path(subject_id)
        vector_db_path = self.subject_manager.get_vector_db_path(subject_id)
        
        pdf_files = list(docs_path.rglob('*.pdf'))
        if not pdf_files:
            print("⚠ No PDF files found, skipping vector DB creation")
            return None
        
        script_path = self.scripts_dir / 'build_vector_db.py'
        result = subprocess.run([
            sys.executable, str(script_path),
            str(docs_path), str(vector_db_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠ Vector DB build warning: {result.stderr}")
            return None
        
        print(f"✓ Vector DB created with {len(pdf_files)} documents")
        return vector_db_path
    
    def run_full_pipeline(self, subject_id):
        try:
            print(f"\n{'='*60}")
            print(f"Starting training pipeline for: {subject_id}")
            print(f"{'='*60}\n")
            
            training_data_path = self.generate_training_data(subject_id)
            
            self.train_layer1_model(subject_id, training_data_path)
            
            self.build_vector_db(subject_id)
            
            self.subject_manager.update_subject(subject_id, model_trained=True)
            
            print(f"\n{'='*60}")
            print(f"✅ Training pipeline completed successfully!")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"Pipeline failed: {str(e)}\n{traceback.format_exc()}"
            print(f"\n❌ {error_msg}")
            self.subject_manager.update_subject(subject_id, model_trained=False)
            raise Exception(error_msg)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python training_pipeline.py <subject_id>")
        sys.exit(1)
    
    subject_id = sys.argv[1]
    pipeline = TrainingPipeline()
    pipeline.run_full_pipeline(subject_id)
