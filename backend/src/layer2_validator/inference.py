import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.layer1_classifier.inference import Layer1Classifier
from src.layer2_validator.mcp_validator import MCPValidator as Layer2Validator


class TwoLayerPipeline:
    def __init__(self, subject_id='data_structures'):
        print(f"Initializing Two-Layer Pipeline for {subject_id}...")
        
        self.subject_id = subject_id
        
        # Load subject name dynamically from syllabus.json
        import json
        from pathlib import Path
        syllabus_path = Path(__file__).parent.parent.parent.parent / 'subjects' / subject_id / 'syllabus.json'
        try:
            with open(syllabus_path, 'r') as f:
                syllabus = json.load(f)
                self.subject_name = syllabus.get('course_name', subject_id.replace('_', ' ').title())
        except:
            self.subject_name = subject_id.replace('_', ' ').title()
        
        # Initialize Layer 1 (DistilBERT classifier)
        try:
            self.layer1 = Layer1Classifier(subject_id=subject_id)
            print("[OK] Layer 1 (DistilBERT) loaded successfully")
        except Exception as e:
            print(f"[ERROR] Layer 1 failed to load: {e}")
            raise
        
        # Initialize Layer 2 (Rule-Based Validator)
        try:
            self.layer2 = Layer2Validator(subject_id=subject_id)
            print("[OK] Layer 2 (Rule-Based Validator) loaded successfully")
        except Exception as e:
            print(f"[ERROR] Layer 2 failed to load: {e}")
            raise
        
        print("[READY] Two-Layer Pipeline ready!")
    
    def process_question(self, question):
        start_time = time.time()
        
        file_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.json']
        is_file_question = any(ext in question.lower() for ext in file_extensions)
        
        if is_file_question:
            import re
            from pathlib import Path
            pattern = r'([\w\-\.]+\.(?:pdf|docx|doc|pptx|ppt|json))'
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                filename = matches[0]
                backend_dir = Path(__file__).parent.parent.parent
                project_root = backend_dir.parent.parent
                ds_folder = project_root / 'DS'
                file_exists = any(ds_folder.rglob(filename))
                if not file_exists:
                    return {
                        'question': question,
                        'layer1_result': 'FAIL',
                        'layer2_result': None,
                        'final_status': 'REJECTED',
                        'message': f'File "{filename}" not found in course materials.',
                        'suggestion': 'Please check the filename or ask about available course topics.',
                        'confidence': 1.0,
                        'total_latency_ms': (time.time() - start_time) * 1000,
                        'layer1_time_ms': 0,
                        'layer2_time_ms': 0
                    }
        
        subject_keywords = []
        try:
            import json
            from pathlib import Path
            syllabus_path = Path(__file__).parent.parent.parent.parent / 'subjects' / self.subject_id / 'syllabus.json'
            with open(syllabus_path, 'r') as f:
                syllabus = json.load(f)
                for unit in syllabus.get('units', []):
                    for topic in unit.get('topics', []):
                        subject_keywords.append(topic.lower())
        except:
            pass
        
        has_subject_keyword = any(keyword in question.lower() for keyword in subject_keywords)
        
        layer1_result = self.layer1.predict(question, return_confidence=True)
        
        # Override Layer 1 if question contains subject keywords
        if not layer1_result['relevant'] and has_subject_keyword:
            layer1_result['relevant'] = True
            layer1_result['label'] = 1
        
        # Override Layer 1 if asking about uploaded files
        if not layer1_result['relevant'] and is_file_question:
            layer1_result['relevant'] = True
            layer1_result['label'] = 1
        
        if not layer1_result['relevant']:
            return {
                'question': question,
                'layer1_result': 'FAIL',
                'layer2_result': None,
                'final_status': 'REJECTED',
                'message': f'This question is not related to {self.subject_name}.',
                'suggestion': f'Please ask questions covered in the {self.subject_name} syllabus.',
                'confidence': layer1_result['confidence'],
                'total_latency_ms': (time.time() - start_time) * 1000,
                'layer1_time_ms': layer1_result['inference_time_ms'],
                'layer2_time_ms': 0
            }
        
        layer2_result = self.layer2.validate_question(question)
        
        if layer2_result.get('final_status') == 'OUT_OF_SYLLABUS':
            return {
                'question': question,
                'layer1_result': 'PASS',
                'layer2_result': 'OUT_OF_SYLLABUS',
                'final_status': 'OUT_OF_SYLLABUS',
                'message': layer2_result['explanation'],
                'suggestion': layer2_result['suggestion'],
                'confidence': layer2_result['confidence'],
                'total_latency_ms': (time.time() - start_time) * 1000,
                'layer1_time_ms': layer1_result['inference_time_ms'],
                'layer2_time_ms': layer2_result['inference_time_ms']
            }
        
        if layer2_result.get('final_status') == 'REJECTED':
            return {
                'question': question,
                'layer1_result': 'PASS',
                'layer2_result': 'FAIL',
                'final_status': 'REJECTED',
                'explanation': layer2_result['explanation'],
                'confidence': layer2_result['confidence'],
                'total_latency_ms': (time.time() - start_time) * 1000,
                'layer1_time_ms': layer1_result['inference_time_ms'],
                'layer2_time_ms': layer2_result['inference_time_ms']
            }
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'question': question,
            'layer1_result': 'PASS',
            'layer2_result': 'IN_SYLLABUS' if layer2_result['status'] == 'VALID' else layer2_result['status'],
            'final_status': layer2_result['status'],
            'explanation': layer2_result['explanation'],
            'warning': layer2_result.get('explanation') if layer2_result['status'] == 'WARNING' else None,
            'confidence': layer2_result['confidence'],
            'total_latency_ms': total_time,
            'layer1_time_ms': layer1_result['inference_time_ms'],
            'layer2_time_ms': layer2_result['inference_time_ms']
        }
