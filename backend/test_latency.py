import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.layer3_rag.inference import generate_answer

# Test questions
test_questions = [
    "What is AVL tree rotation?",
    "Explain binary search tree",
    "How does hashing work?",
    "What is Dijkstra's algorithm?",
    "Explain quicksort algorithm"
]

print("=" * 60)
print("LAYER 3 RAG LATENCY TEST")
print("=" * 60)
print(f"\nTesting {len(test_questions)} questions...\n")

latencies = []

for i, question in enumerate(test_questions, 1):
    print(f"[{i}/{len(test_questions)}] Testing: {question}")
    
    start = time.time()
    answer = generate_answer(question)
    latency = time.time() - start
    latencies.append(latency)
    
    print(f"   Latency: {latency:.2f}s")
    print(f"   Answer: {answer[:100]}...")
    print()

print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Average Latency: {sum(latencies)/len(latencies):.2f}s")
print(f"Min Latency: {min(latencies):.2f}s")
print(f"Max Latency: {max(latencies):.2f}s")
print(f"Total Time: {sum(latencies):.2f}s")
print()
print("Optimization: top_k=2, shorter prompt")
print("Previous avg: ~12s | Current avg: ~{:.2f}s".format(sum(latencies)/len(latencies)))
print("Improvement: {:.1f}%".format((12 - sum(latencies)/len(latencies)) / 12 * 100))
