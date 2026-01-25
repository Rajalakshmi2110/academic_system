import json
import time
from pathlib import Path
from src.layer1_classifier.inference import Layer1Classifier
from src.layer2_validator.flan_t5_validator import FLANT5Validator

class TwoLayerPipeline:
    def __init__(self):
        """Initialize both Layer 1 and Layer 2 models"""
        print("Initializing Two-Layer Academic Doubt Clarification System...")
        
        # Initialize Layer 1 (DistilBERT)
        try:
            self.layer1 = Layer1Classifier()
            print("✓ Layer 1 (DistilBERT) loaded successfully")
        except Exception as e:
            print(f"✗ Layer 1 failed to load: {e}")
            raise
        
        # Initialize Layer 2 (FLAN-T5)
        try:
            self.layer2 = FLANT5Validator()
            print("✓ Layer 2 (FLAN-T5) loaded successfully")
        except Exception as e:
            print(f"✗ Layer 2 failed to load: {e}")
            raise
        
        print("🚀 Two-Layer Pipeline ready!")
    
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
            # Question is out-of-syllabus - return immediately
            return {
                'question': question,
                'layer1_result': 'OUT_OF_SYLLABUS',
                'layer2_result': None,
                'final_status': 'OUT_OF_SYLLABUS',
                'message': 'This question is not related to the CA3104 Computer Networks syllabus.',
                'suggestion': 'Please ask questions about network protocols, architectures, or concepts covered in Units I-V.',
                'confidence': layer1_result['confidence'],
                'total_latency_ms': (time.time() - start_time) * 1000,
                'layer1_time_ms': layer1_result['inference_time_ms'],
                'layer2_time_ms': 0
            }
        
        # Layer 2: Deep Academic Validation
        layer2_result = self.layer2.validate_question(question)
        
        # Format final response
        total_time = (time.time() - start_time) * 1000
        
        return {
            'question': question,
            'layer1_result': 'IN_SYLLABUS',
            'layer2_result': layer2_result['status'],
            'final_status': layer2_result['status'],
            'explanation': layer2_result['explanation'],
            'confidence': layer2_result['confidence'],
            'total_latency_ms': total_time,
            'layer1_time_ms': layer1_result['inference_time_ms'],
            'layer2_time_ms': layer2_result['inference_time_ms']
        }
    
    def batch_process(self, questions):
        """Process multiple questions through the pipeline"""
        results = []
        for question in questions:
            result = self.process_question(question)
            results.append(result)
        return results
    
    def get_statistics(self, results):
        """Generate statistics from batch processing results"""
        total_questions = len(results)
        out_of_syllabus = sum(1 for r in results if r['final_status'] == 'OUT_OF_SYLLABUS')
        valid = sum(1 for r in results if r['final_status'] == 'VALID')
        warning = sum(1 for r in results if r['final_status'] == 'WARNING')
        rejected = sum(1 for r in results if r['final_status'] == 'REJECTED')
        
        avg_total_time = sum(r['total_latency_ms'] for r in results) / total_questions
        avg_layer1_time = sum(r['layer1_time_ms'] for r in results) / total_questions
        avg_layer2_time = sum(r['layer2_time_ms'] for r in results if r['layer2_time_ms'] > 0)
        if avg_layer2_time:
            avg_layer2_time = avg_layer2_time / sum(1 for r in results if r['layer2_time_ms'] > 0)
        else:
            avg_layer2_time = 0
        
        return {
            'total_questions': total_questions,
            'distribution': {
                'out_of_syllabus': out_of_syllabus,
                'valid': valid,
                'warning': warning,
                'rejected': rejected
            },
            'percentages': {
                'out_of_syllabus': (out_of_syllabus / total_questions) * 100,
                'valid': (valid / total_questions) * 100,
                'warning': (warning / total_questions) * 100,
                'rejected': (rejected / total_questions) * 100
            },
            'performance': {
                'avg_total_latency_ms': avg_total_time,
                'avg_layer1_latency_ms': avg_layer1_time,
                'avg_layer2_latency_ms': avg_layer2_time
            }
        }

def demo_pipeline():
    """Comprehensive demo of the two-layer pipeline"""
    try:
        pipeline = TwoLayerPipeline()
        
        # Test questions covering all scenarios
        test_questions = [
            # Should be OUT_OF_SYLLABUS (Layer 1 rejects)
            "What's the best programming language for AI?",
            "How do I fix my printer connection?",
            
            # Should be VALID (Layer 1 accepts, Layer 2 validates)
            "Explain the TCP three-way handshake process",
            "Compare CSMA/CD and CSMA/CA protocols",
            
            # Should be WARNING (Layer 1 accepts, Layer 2 finds issues)
            "Explain network protocols and security",
            "How does TCP work with everything?",
            
            # Should be REJECTED (Layer 1 accepts, Layer 2 finds errors)
            "TCP uses 5-way handshake for security",
            "Ethernet prevents all network collisions"
        ]
        
        print("\n=== TWO-LAYER PIPELINE DEMO ===")
        
        results = []
        for i, question in enumerate(test_questions, 1):
            print(f"\nTest {i}/{len(test_questions)}:")
            print(f"Question: {question}")
            
            result = pipeline.process_question(question)
            results.append(result)
            
            print(f"Layer 1: {result['layer1_result']}")
            if result['layer2_result']:
                print(f"Layer 2: {result['layer2_result']}")
            print(f"Final Status: {result['final_status']}")
            
            if 'explanation' in result:
                print(f"Explanation: {result['explanation']}")
            elif 'message' in result:
                print(f"Message: {result['message']}")
            
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Total Time: {result['total_latency_ms']:.2f} ms")
            print("-" * 70)
        
        # Generate statistics
        stats = pipeline.get_statistics(results)
        
        print("\n=== PIPELINE STATISTICS ===")
        print(f"Total Questions: {stats['total_questions']}")
        print(f"Out-of-Syllabus: {stats['distribution']['out_of_syllabus']} ({stats['percentages']['out_of_syllabus']:.1f}%)")
        print(f"Valid: {stats['distribution']['valid']} ({stats['percentages']['valid']:.1f}%)")
        print(f"Warning: {stats['distribution']['warning']} ({stats['percentages']['warning']:.1f}%)")
        print(f"Rejected: {stats['distribution']['rejected']} ({stats['percentages']['rejected']:.1f}%)")
        
        print(f"\nPerformance:")
        print(f"Average Total Latency: {stats['performance']['avg_total_latency_ms']:.2f} ms")
        print(f"Average Layer 1 Time: {stats['performance']['avg_layer1_latency_ms']:.2f} ms")
        print(f"Average Layer 2 Time: {stats['performance']['avg_layer2_latency_ms']:.2f} ms")
        
    except Exception as e:
        print(f"Pipeline demo failed: {e}")

if __name__ == "__main__":
    demo_pipeline()