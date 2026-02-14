import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.layer1_classifier.inference import Layer1Classifier
from src.layer2_validator.mcp_validator import MCPValidator as Layer2Validator

# use Rules (backup)
#from src.layer2_validator.rule_based_validator import RuleBasedValidator as Layer2Validator


class TwoLayerPipeline:
    def __init__(self, layer1_model_path='models/layer1_distilbert'):
        """Initialize both Layer 1 and Layer 2 models"""
        print("Initializing Two-Layer Academic Doubt Clarification System...")
        
        # Initialize Layer 1 (DistilBERT)
        try:
            self.layer1 = Layer1Classifier(model_path=layer1_model_path)
            print("[OK] Layer 1 (DistilBERT) loaded successfully")
        except Exception as e:
            print(f"[ERROR] Layer 1 failed to load: {e}")
            raise
        
        # Initialize Layer 2 (MCP Validator with GPT-4o)
        try:
            self.layer2 = Layer2Validator()
            print("[OK] Layer 2 (MCP Validator) loaded successfully")
        except Exception as e:
            print(f"[ERROR] Layer 2 failed to load: {e}")
            raise
        
        print("[READY] Two-Layer Pipeline ready!")
    
    def process_question(self, question):
        """
        Process a student question through the complete two-layer pipeline
        
        Args:
            question (str): Student question to validate
            
        Returns:
            dict: Complete validation result
        """
        start_time = time.time()
        
        # Layer 1: Syllabus Relevance Check
        layer1_result = self.layer1.predict(question, return_confidence=True)
        
        if not layer1_result['relevant']:
            # Question is not DS-related - return immediately
            return {
                'question': question,
                'layer1_result': 'FAIL',
                'layer2_result': None,
                'final_status': 'REJECTED',
                'message': 'This question is not related to Data Structures.',
                'suggestion': 'Please ask questions about arrays, linked lists, trees, graphs, sorting, searching, or other data structures topics.',
                'confidence': layer1_result['confidence'],
                'total_latency_ms': (time.time() - start_time) * 1000,
                'layer1_time_ms': layer1_result['inference_time_ms'],
                'layer2_time_ms': 0
            }
        
        # Layer 2: Deep Academic Validation
        layer2_result = self.layer2.validate_question(question)
        
        # Check if Layer 2 caught out-of-syllabus
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
        
        # Check if Layer 2 rejected
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
        
        # Format final response
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
