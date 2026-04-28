"""
Test all 68 questions across 3 subjects and collect metrics.
Usage: python scripts/test_all_subjects.py [--skip-rag] [--base-url URL]
  --skip-rag: Only test Layer 1 & 2 (much faster, skips ~10s/question RAG)
  --base-url:  Default http://localhost:5001
"""
import requests, json, time, sys
from collections import defaultdict

BASE_URL = "http://localhost:5001"
SKIP_RAG = False

for arg in sys.argv[1:]:
    if arg == "--skip-rag":
        SKIP_RAG = True
    elif arg.startswith("--base-url="):
        BASE_URL = arg.split("=", 1)[1]

# ── Test Questions ──────────────────────────────────────────────
TEST_CASES = [
    # === DATA STRUCTURES (CA3101) ===
    # VALID
    ("data_structures", "What is the difference between a singly linked list and a doubly linked list?", "VALID"),
    ("data_structures", "Explain AVL tree rotations with an example.", "VALID"),
    ("data_structures", "How does Kruskal's algorithm find the minimum spanning tree?", "VALID"),
    ("data_structures", "What is the time complexity of quick sort in the worst case?", "VALID"),
    ("data_structures", "Explain collision resolution techniques in hashing.", "VALID"),
    ("data_structures", "How does BFS differ from DFS in graph traversal?", "VALID"),
    ("data_structures", "What are the applications of stacks and queues?", "VALID"),
    ("data_structures", "Explain binary heap insertion and deletion.", "VALID"),
    ("data_structures", "What is a 2-3 tree and how does insertion work?", "VALID"),
    ("data_structures", "Describe sequential vs indexed file organization.", "VALID"),
    # WARNING
    ("data_structures", "Is it true that AVL trees allow a balance factor of 5?", "WARNING"),
    ("data_structures", "Quick sort has O(n) worst case time complexity, right?", "WARNING"),
    ("data_structures", "Linked lists support O(1) random access like arrays, correct?", "WARNING"),
    ("data_structures", "Prim's algorithm works on unweighted graphs, right?", "WARNING"),
    # OUT_OF_SYLLABUS
    ("data_structures", "Explain Red-Black trees and their properties.", "OUT_OF_SYLLABUS"),
    ("data_structures", "What is a B+ tree and how is it used in databases?", "OUT_OF_SYLLABUS"),
    ("data_structures", "Explain the Trie data structure for string matching.", "OUT_OF_SYLLABUS"),
    ("data_structures", "How does a skip list work?", "OUT_OF_SYLLABUS"),
    # REJECTED
    ("data_structures", "What is photosynthesis?", "REJECTED"),
    ("data_structures", "Who won the FIFA World Cup in 2022?", "REJECTED"),
    ("data_structures", "How do I make pasta?", "REJECTED"),
    ("data_structures", "asdfghjkl random gibberish 123", "REJECTED"),

    # === OPERATING SYSTEM (BX3004) ===
    # VALID
    ("operating_system", "What are the different types of system calls?", "VALID"),
    ("operating_system", "Explain the difference between preemptive and non-preemptive scheduling.", "VALID"),
    ("operating_system", "What is the critical section problem and how do semaphores solve it?", "VALID"),
    ("operating_system", "Explain demand paging and page replacement algorithms.", "VALID"),
    ("operating_system", "What is thrashing and how can it be prevented?", "VALID"),
    ("operating_system", "Describe the Banker's algorithm for deadlock avoidance.", "VALID"),
    ("operating_system", "What are the different disk scheduling algorithms?", "VALID"),
    ("operating_system", "Explain contiguous vs linked allocation methods for files.", "VALID"),
    ("operating_system", "What is the difference between paging and segmentation?", "VALID"),
    ("operating_system", "How does inter-process communication work using shared memory?", "VALID"),
    # WARNING
    ("operating_system", "Is it true that Round Robin scheduling doesn't use time quantum?", "WARNING"),
    ("operating_system", "Deadlocks can only occur with 2 processes, right?", "WARNING"),
    ("operating_system", "Virtual memory means we don't need RAM at all, correct?", "WARNING"),
    # OUT_OF_SYLLABUS
    ("operating_system", "Explain how Docker containers use OS-level virtualization.", "OUT_OF_SYLLABUS"),
    ("operating_system", "What is the Windows Registry and how does it work?", "OUT_OF_SYLLABUS"),
    ("operating_system", "How does the Linux kernel handle device drivers?", "OUT_OF_SYLLABUS"),
    # REJECTED
    ("operating_system", "What is the capital of France?", "REJECTED"),
    ("operating_system", "Explain Newton's third law of motion.", "REJECTED"),
    ("operating_system", "How to train a neural network?", "REJECTED"),
    ("operating_system", "hello hello hello test test", "REJECTED"),

    # === COMPUTER NETWORKS AND MANAGEMENT (CA3104) ===
    # VALID
    ("computer_networks_and_management", "Compare the OSI and TCP/IP reference models.", "VALID"),
    ("computer_networks_and_management", "Explain CSMA/CD and how Ethernet uses it.", "VALID"),
    ("computer_networks_and_management", "What is subnetting and how does CIDR work?", "VALID"),
    ("computer_networks_and_management", "Explain the difference between TCP and UDP.", "VALID"),
    ("computer_networks_and_management", "How does DNS resolve domain names?", "VALID"),
    ("computer_networks_and_management", "What is SNMP and how is it used in network management?", "VALID"),
    ("computer_networks_and_management", "Explain distance vector vs link state routing algorithms.", "VALID"),
    ("computer_networks_and_management", "What is the purpose of NAT and DHCP?", "VALID"),
    ("computer_networks_and_management", "Describe the functions of hubs, bridges, switches, and routers.", "VALID"),
    ("computer_networks_and_management", "How does the TCP three-way handshake work?", "VALID"),
    # WARNING
    ("computer_networks_and_management", "UDP provides reliable delivery with error correction, right?", "WARNING"),
    ("computer_networks_and_management", "Is it true that IPv4 addresses are 128 bits long?", "WARNING"),
    ("computer_networks_and_management", "Routers operate at the data link layer, correct?", "WARNING"),
    # OUT_OF_SYLLABUS
    ("computer_networks_and_management", "Explain how TLS/SSL encryption works in HTTPS.", "OUT_OF_SYLLABUS"),
    ("computer_networks_and_management", "What is MPLS and how does it improve network performance?", "OUT_OF_SYLLABUS"),
    ("computer_networks_and_management", "How does a CDN like CloudFront distribute content?", "OUT_OF_SYLLABUS"),
    # REJECTED
    ("computer_networks_and_management", "What is the Pythagorean theorem?", "REJECTED"),
    ("computer_networks_and_management", "How do vaccines work?", "REJECTED"),
    ("computer_networks_and_management", "Explain supply and demand in economics.", "REJECTED"),
    ("computer_networks_and_management", "lkjhgfdsa qwerty zxcvbn", "REJECTED"),

    # === CROSS-SUBJECT CONFUSION ===
    ("data_structures", "What is paging in OS?", "REJECTED"),
    ("operating_system", "Explain TCP congestion control", "REJECTED"),
    ("computer_networks_and_management", "What is a binary search tree?", "REJECTED"),
    ("data_structures", "Explain OSPF routing protocol", "REJECTED"),
    ("computer_networks_and_management", "What is deadlock?", "REJECTED"),
    ("operating_system", "How does DNS work?", "REJECTED"),
]

# ── Run Tests ───────────────────────────────────────────────────
def send_question(subject_id, question):
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", json={
            "question": question,
            "subject_id": subject_id,
            "show_steps": True
        }, timeout=120)
        return resp.json()
    except Exception as e:
        return {"error": str(e), "final_status": "ERROR"}

results = []
total = len(TEST_CASES)

print(f"\n{'='*70}")
print(f"  TESTING {total} QUESTIONS | RAG: {'OFF (Layer 1&2 only)' if SKIP_RAG else 'ON'}")
print(f"  Backend: {BASE_URL}")
print(f"{'='*70}\n")

for i, (subject, question, expected) in enumerate(TEST_CASES, 1):
    # Skip RAG-bound questions if --skip-rag (only send questions that won't reach Layer 3)
    # Actually we always send — the API handles it. But with skip-rag we could skip VALID/WARNING
    # For now, send all and just measure.
    
    short_q = question[:55] + "..." if len(question) > 55 else question
    print(f"[{i:2d}/{total}] {subject[:15]:15s} | {short_q:58s} | ", end="", flush=True)
    
    start = time.time()
    resp = send_question(subject, question)
    elapsed = (time.time() - start) * 1000
    
    actual = resp.get("final_status", resp.get("status", "ERROR")).upper()
    # Normalize: 'success' from Layer 3 means it was VALID
    if actual == "SUCCESS":
        actual = "VALID"
    
    match = "✅" if actual == expected else "❌"
    print(f"{actual:16s} (expect {expected:16s}) {match}  [{elapsed:.0f}ms]")
    
    results.append({
        "subject": subject,
        "question": question,
        "expected": expected,
        "actual": actual,
        "match": actual == expected,
        "elapsed_ms": elapsed,
        "layer1": resp.get("layer1_result"),
        "layer2": resp.get("layer2_result") or resp.get("final_status"),
        "confidence": resp.get("confidence_score"),
        "steps": resp.get("intermediate_steps", {}),
        "warning": resp.get("warning"),
    })

# ── Metrics Summary ─────────────────────────────────────────────
print(f"\n{'='*70}")
print("  METRICS SUMMARY")
print(f"{'='*70}")

# Overall accuracy
correct = sum(1 for r in results if r["match"])
print(f"\n  Overall Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")

# Per-subject breakdown
subjects = ["data_structures", "operating_system", "computer_networks_and_management"]
subject_names = {"data_structures": "Data Structures", "operating_system": "Operating System",
                 "computer_networks_and_management": "Computer Networks"}

for sid in subjects:
    subj_results = [r for r in results if r["subject"] == sid]
    subj_correct = sum(1 for r in subj_results if r["match"])
    print(f"\n  ── {subject_names[sid]} ──")
    print(f"  Accuracy: {subj_correct}/{len(subj_results)} ({subj_correct/len(subj_results)*100:.1f}%)")
    
    # Status distribution
    status_counts = defaultdict(int)
    for r in subj_results:
        status_counts[r["actual"]] += 1
    print(f"  Status Distribution: {dict(status_counts)}")

# Cross-subject results
cross = [r for r in results if r in results[-6:]]  # last 6 are cross-subject
cross_results = results[-6:]
cross_correct = sum(1 for r in cross_results if r["match"])
print(f"\n  ── Cross-Subject Confusion ──")
print(f"  Accuracy: {cross_correct}/6 ({cross_correct/6*100:.1f}%)")

# Latency stats
def lat_stats(lst):
    if not lst: return "N/A"
    return f"avg={sum(lst)/len(lst):.0f}ms  min={min(lst):.0f}ms  max={max(lst):.0f}ms"

all_l1 = [r["steps"].get("layer1", {}).get("latency_ms", 0) for r in results if r["steps"].get("layer1")]
all_l2 = [r["steps"].get("layer2", {}).get("latency_ms", 0) for r in results if r["steps"].get("layer2")]
all_l3 = [r["steps"].get("layer3", {}).get("latency_ms", 0) for r in results if r["steps"].get("layer3")]
all_total = [r["elapsed_ms"] for r in results]

print(f"\n  ── Latency ──")
print(f"  Layer 1 (Classifier): {lat_stats(all_l1)}")
print(f"  Layer 2 (Syllabus):   {lat_stats(all_l2)}")
print(f"  Layer 3 (RAG):        {lat_stats(all_l3)}")
print(f"  Total (end-to-end):   {lat_stats(all_total)}")

# Confidence scores (only for VALID/WARNING that got answers)
conf_scores = [r["confidence"] for r in results if r["confidence"] is not None]
if conf_scores:
    print(f"\n  ── Confidence Scores ──")
    print(f"  Avg: {sum(conf_scores)/len(conf_scores):.2f}  Min: {min(conf_scores):.2f}  Max: {max(conf_scores):.2f}")
    low = sum(1 for c in conf_scores if c < 0.6)
    print(f"  Low confidence (<0.6): {low}/{len(conf_scores)}")

# Mismatches detail
mismatches = [r for r in results if not r["match"]]
if mismatches:
    print(f"\n  ── Mismatches ({len(mismatches)}) ──")
    for r in mismatches:
        print(f"  ❌ [{r['subject'][:12]}] \"{r['question'][:50]}...\"")
        print(f"     Expected: {r['expected']}  Got: {r['actual']}  L1={r['layer1']}  L2={r['layer2']}")
else:
    print(f"\n  🎉 All {total} questions matched expected results!")

# Save full results to JSON
output_path = "scripts/test_results.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Full results saved to: {output_path}")
print(f"{'='*70}\n")
