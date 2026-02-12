import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.layer3_rag.rag_pipeline import RAGPipeline

def evaluate_layer3():
    """Evaluate Layer 3 RAG Pipeline"""
    vector_db_path = Path('data/vector_db')
    rag = RAGPipeline(vector_db_path)
    
    test_cases = [
        {'question': 'What is a stack?', 'topic': 'Stack'},
        {'question': 'Explain binary search tree', 'topic': 'BST'},
        {'question': 'How does BFS algorithm work?', 'topic': 'Graph'},
        {'question': 'What is AVL tree rotation?', 'topic': 'AVL Tree'},
        {'question': 'Explain quicksort algorithm', 'topic': 'Sorting'},
        {'question': 'What is hashing?', 'topic': 'Hashing'},
        {'question': 'Explain linked list', 'topic': 'Linked List'},
        {'question': 'What is a heap data structure?', 'topic': 'Heap'},
    ]
    
    results = {
        'successful_answers': 0,
        'failed_answers': 0,
        'latencies': [],
        'answer_lengths': []
    }
    
    print("=== LAYER 3 EVALUATION (RAG Pipeline) ===")
    print(f"Testing {len(test_cases)} questions...\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['question']}")
        
        try:
            start = time.time()
            result = rag.answer_question(case['question'])
            latency = (time.time() - start) * 1000
            
            if result['status'] == 'success':
                answer = result['answer']
                results['latencies'].append(latency)
                results['answer_lengths'].append(len(answer))
                results['successful_answers'] += 1
                
                print(f"   ✓ Generated ({latency:.0f}ms, {len(answer)} chars)")
                print(f"   Preview: {answer[:100]}...")
            else:
                results['failed_answers'] += 1
                print(f"   ✗ Failed: {result['message']}")
            
        except Exception as e:
            results['failed_answers'] += 1
            print(f"   ✗ Failed: {str(e)}")
        
        print()
    
    # Calculate metrics
    success_rate = results['successful_answers'] / len(test_cases)
    avg_latency = sum(results['latencies']) / len(results['latencies']) if results['latencies'] else 0
    avg_answer_length = sum(results['answer_lengths']) / len(results['answer_lengths']) if results['answer_lengths'] else 0
    
    print(f"=== RESULTS ===")
    print(f"Success Rate: {success_rate:.2%} ({results['successful_answers']}/{len(test_cases)})")
    print(f"Failed: {results['failed_answers']}")
    print(f"Avg Latency: {avg_latency:.2f} ms ({avg_latency/1000:.1f}s)")
    print(f"Min Latency: {min(results['latencies']):.2f} ms" if results['latencies'] else "N/A")
    print(f"Max Latency: {max(results['latencies']):.2f} ms" if results['latencies'] else "N/A")
    print(f"Avg Answer Length: {avg_answer_length:.0f} characters")
    
    # Save metrics
    metrics = {
        "success_rate": float(success_rate),
        "successful_answers": results['successful_answers'],
        "failed_answers": results['failed_answers'],
        "total_samples": len(test_cases),
        "avg_latency_ms": float(avg_latency),
        "min_latency_ms": float(min(results['latencies'])) if results['latencies'] else None,
        "max_latency_ms": float(max(results['latencies'])) if results['latencies'] else None,
        "avg_answer_length": float(avg_answer_length),
        "latencies": [float(l) for l in results['latencies']]
    }
    
    output_path = Path('src/layer3_rag/layer3_metrics.json')
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✓ Metrics saved to {output_path}")
    return success_rate >= 0.9

if __name__ == "__main__":
    success = evaluate_layer3()
    print(f"\nOverall evaluation: {'PASS' if success else 'FAIL'}")
