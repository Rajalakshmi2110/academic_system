import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.layer2_validator.mcp_validator import MCPValidator

def evaluate_layer2():
    """Evaluate Layer 2 MCP Validator with Groq"""
    validator = MCPValidator()
    
    test_cases = [
        # VALID cases
        {'question': 'What is a linked list?', 'expected': 'VALID'},
        {'question': 'Explain Dijkstra algorithm', 'expected': 'VALID'},
        {'question': 'How does merge sort work?', 'expected': 'VALID'},
        {'question': 'What is a B-tree?', 'expected': 'VALID'},
        {'question': 'Explain hash collision resolution', 'expected': 'VALID'},
        {'question': 'wht is heep?', 'expected': 'VALID'},  # typo but still valid
        
        # WARNING cases (incorrect facts but should still answer)
        {'question': 'Queue is LIFO correct?', 'expected': 'WARNING'},
        {'question': 'Bubble sort is O(n log n) right?', 'expected': 'WARNING'},
        {'question': 'Trees can have cycles?', 'expected': 'WARNING'},
        
        # OUT_OF_SYLLABUS cases (DS topics not in CA3101)
        {'question': 'What is a splay tree?', 'expected': 'OUT_OF_SYLLABUS'},
        {'question': 'Explain suffix tree', 'expected': 'OUT_OF_SYLLABUS'},
        {'question': 'How does segment tree work?', 'expected': 'OUT_OF_SYLLABUS'},
        
        # REJECTED cases (non-DS topics and gibberish)
        {'question': 'What is Kubernetes?', 'expected': 'REJECTED'},
        {'question': 'How to use PostgreSQL?', 'expected': 'REJECTED'},
        {'question': 'Explain GraphQL', 'expected': 'REJECTED'},
        {'question': 'zxcvbnm', 'expected': 'REJECTED'},
        {'question': '!!!!!!', 'expected': 'REJECTED'},
    ]
    
    results = {
        'valid': 0,
        'warning': 0,
        'out_of_syllabus': 0,
        'rejected': 0,
        'correct_predictions': 0,
        'latencies': []
    }
    
    print("=== LAYER 2 EVALUATION (Groq MCP Validator) ===")
    print(f"Testing {len(test_cases)} cases...\n")
    
    for i, case in enumerate(test_cases, 1):
        start = time.time()
        result = validator.validate_question(case['question'])
        latency = (time.time() - start) * 1000
        results['latencies'].append(latency)
        
        # Handle both 'status' and 'final_status' keys
        status = result.get('status') or result.get('final_status', 'UNKNOWN')
        expected = case['expected']
        correct = '✓' if status == expected else '✗'
        
        print(f"{i}. {case['question'][:50]}")
        print(f"   Expected: {expected}, Got: {status} {correct} ({latency:.0f}ms)")
        
        # Count statuses
        if status == 'VALID':
            results['valid'] += 1
        elif status == 'WARNING':
            results['warning'] += 1
        elif status == 'OUT_OF_SYLLABUS':
            results['out_of_syllabus'] += 1
        elif status == 'REJECTED':
            results['rejected'] += 1
        
        if status == expected:
            results['correct_predictions'] += 1
    
    # Calculate metrics
    accuracy = results['correct_predictions'] / len(test_cases)
    avg_latency = sum(results['latencies']) / len(results['latencies'])
    
    print(f"\n=== RESULTS ===")
    print(f"Accuracy: {accuracy:.2%} ({results['correct_predictions']}/{len(test_cases)})")
    print(f"VALID: {results['valid']}")
    print(f"WARNING: {results['warning']}")
    print(f"OUT_OF_SYLLABUS: {results['out_of_syllabus']}")
    print(f"REJECTED: {results['rejected']}")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"Min Latency: {min(results['latencies']):.2f} ms")
    print(f"Max Latency: {max(results['latencies']):.2f} ms")
    
    # Save metrics
    metrics = {
        "accuracy": float(accuracy),
        "correct_predictions": results['correct_predictions'],
        "total_samples": len(test_cases),
        "status_counts": {
            "valid": results['valid'],
            "warning": results['warning'],
            "out_of_syllabus": results['out_of_syllabus'],
            "rejected": results['rejected']
        },
        "avg_latency_ms": float(avg_latency),
        "min_latency_ms": float(min(results['latencies'])),
        "max_latency_ms": float(max(results['latencies'])),
        "latencies": [float(l) for l in results['latencies']]
    }
    
    output_path = Path('src/layer2_validator/layer2_metrics.json')
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✓ Metrics saved to {output_path}")
    return accuracy >= 0.8

if __name__ == "__main__":
    success = evaluate_layer2()
    print(f"\nOverall evaluation: {'PASS' if success else 'FAIL'}")
