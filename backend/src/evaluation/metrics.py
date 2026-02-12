import json
import time
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.layer1_classifier.inference import Layer1Classifier
from src.layer2_validator.inference import TwoLayerPipeline
from src.layer3_rag.inference import generate_answer


class SystemEvaluator:
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / 'models' / 'layer1_distilbert'
        
        self.layer1 = Layer1Classifier(model_path=str(model_path))
        self.pipeline = TwoLayerPipeline(layer1_model_path=str(model_path))
        self.project_root = project_root
    
    def evaluate_layer1(self, test_file='data/processed/test.json'):
        """Evaluate Layer 1 classifier performance"""
        test_file_path = self.project_root / test_file
        with open(test_file_path, 'r') as f:
            test_data = json.load(f)
        
        y_true = [item['label'] for item in test_data]
        y_pred = []
        latencies = []
        
        for item in test_data:
            result = self.layer1.predict(item['question'])
            y_pred.append(result['label'])
            latencies.append(result['inference_time_ms'])
        
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        cm = confusion_matrix(y_true, y_pred)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'total_samples': len(test_data)
        }
    
    def evaluate_layer2(self, test_cases):
        """Evaluate Layer 2 rule-based validation"""
        results = {
            'rejected': 0,
            'out_of_syllabus': 0,
            'warnings': 0,
            'valid': 0,
            'latencies': []
        }
        
        for case in test_cases:
            start = time.time()
            result = self.pipeline.process_question(case['question'])
            latency = (time.time() - start) * 1000
            results['latencies'].append(latency)
            
            status = result['final_status']
            if status == 'REJECTED':
                results['rejected'] += 1
            elif status == 'OUT_OF_SYLLABUS':
                results['out_of_syllabus'] += 1
            elif status == 'WARNING':
                results['warnings'] += 1
            elif status == 'VALID':
                results['valid'] += 1
        
        results['avg_latency_ms'] = sum(results['latencies']) / len(results['latencies'])
        results['total_samples'] = len(test_cases)
        return results
    
    def evaluate_end_to_end(self, test_cases):
        """Evaluate complete pipeline latency"""
        latencies = []
        
        for case in test_cases:
            start = time.time()
            result = self.pipeline.process_question(case['question'])
            
            if result['final_status'] == 'VALID':
                answer = generate_answer(case['question'])
            
            total_time = (time.time() - start) * 1000
            latencies.append(total_time)
        
        return {
            'avg_latency_ms': sum(latencies) / len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'total_samples': len(test_cases)
        }


def run_evaluation():
    print("=" * 60)
    print("SYSTEM EVALUATION METRICS")
    print("=" * 60)
    
    evaluator = SystemEvaluator()
    
    # Layer 1 Evaluation
    print("\n[Layer 1: Binary Classifier]")
    layer1_metrics = evaluator.evaluate_layer1()
    print(f"Accuracy:  {layer1_metrics['accuracy']:.4f}")
    print(f"Precision: {layer1_metrics['precision']:.4f}")
    print(f"Recall:    {layer1_metrics['recall']:.4f}")
    print(f"F1-Score:  {layer1_metrics['f1_score']:.4f}")
    print(f"Avg Latency: {layer1_metrics['avg_latency_ms']:.2f} ms")
    print(f"Confusion Matrix:\n{layer1_metrics['confusion_matrix']}")
    
    # Layer 2 Evaluation
    print("\n[Layer 2: Rule-Based Validator]")
    layer2_test_cases = [
        {'question': 'asdfghjkl', 'expected': 'REJECTED'},
        {'question': 'What is a skip list?', 'expected': 'OUT_OF_SYLLABUS'},
        {'question': 'Explain binary search tree', 'expected': 'VALID'},
        {'question': 'What is AWS Lambda?', 'expected': 'OUT_OF_SYLLABUS'},
        {'question': 'Describe AVL tree rotation', 'expected': 'VALID'},
    ]
    layer2_metrics = evaluator.evaluate_layer2(layer2_test_cases)
    print(f"Valid: {layer2_metrics['valid']}")
    print(f"Warnings: {layer2_metrics['warnings']}")
    print(f"Rejected: {layer2_metrics['rejected']}")
    print(f"Out-of-Syllabus: {layer2_metrics['out_of_syllabus']}")
    print(f"Avg Latency: {layer2_metrics['avg_latency_ms']:.2f} ms")
    
    # End-to-End Evaluation
    print("\n[End-to-End Pipeline]")
    e2e_test_cases = [
        {'question': 'What is a binary search tree?'},
        {'question': 'Explain AVL tree balancing'},
        {'question': 'What is hashing?'},
    ]
    e2e_metrics = evaluator.evaluate_end_to_end(e2e_test_cases)
    print(f"Avg Latency: {e2e_metrics['avg_latency_ms']:.2f} ms")
    print(f"Min Latency: {e2e_metrics['min_latency_ms']:.2f} ms")
    print(f"Max Latency: {e2e_metrics['max_latency_ms']:.2f} ms")
    
    print("\n" + "=" * 60)
    
    # Save results
    results = {
        'layer1': layer1_metrics,
        'layer2': layer2_metrics,
        'end_to_end': e2e_metrics
    }
    
    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to evaluation_results.json")
    print("\nNote: Run individual layer evaluations for detailed metrics:")
    print("  - python src/layer1_classifier/evaluate.py")
    print("  - python src/layer2_validator/evaluate.py")
    print("  - python src/layer3_rag/evaluate.py")


if __name__ == '__main__':
    run_evaluation()
