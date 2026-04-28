import requests
import time
import json

API = "http://localhost:5001/api/chat"

test_questions = [
    # === DATA STRUCTURES (valid) ===
    {"question": "What is a linked list?", "subject_id": "data_structures"},
    {"question": "Explain stack push and pop operations", "subject_id": "data_structures"},
    {"question": "What is a binary search tree?", "subject_id": "data_structures"},
    {"question": "How does queue work?", "subject_id": "data_structures"},
    {"question": "What is AVL tree rotation?", "subject_id": "data_structures"},
    {"question": "Explain doubly linked list", "subject_id": "data_structures"},
    {"question": "What are applications of stacks?", "subject_id": "data_structures"},
    # DS warnings (wrong facts)
    {"question": "Is bubble sort O(n log n)?", "subject_id": "data_structures"},
    {"question": "Stack is FIFO right?", "subject_id": "data_structures"},
    {"question": "Is binary search O(n)?", "subject_id": "data_structures"},

    # === OPERATING SYSTEM (valid) ===
    {"question": "What is a process in operating system?", "subject_id": "operating_system"},
    {"question": "Explain CPU scheduling algorithms", "subject_id": "operating_system"},
    {"question": "What are system calls?", "subject_id": "operating_system"},
    {"question": "Explain process scheduling", "subject_id": "operating_system"},
    {"question": "What is inter process communication?", "subject_id": "operating_system"},
    {"question": "Explain virtualization in OS", "subject_id": "operating_system"},
    {"question": "What is multiple processor scheduling?", "subject_id": "operating_system"},

    # === COMPUTER NETWORKS (valid) ===
    {"question": "What is OSI model?", "subject_id": "computer_networks_and_management"},
    {"question": "Explain TCP/IP reference model", "subject_id": "computer_networks_and_management"},
    {"question": "What are networking devices?", "subject_id": "computer_networks_and_management"},
    {"question": "Explain the role of routers and switches", "subject_id": "computer_networks_and_management"},
    {"question": "What is layered architecture in networking?", "subject_id": "computer_networks_and_management"},
    {"question": "Explain transmission errors", "subject_id": "computer_networks_and_management"},
    {"question": "What are edge and core networks?", "subject_id": "computer_networks_and_management"},
]

print(f"Sending {len(test_questions)} test questions...\n")

for i, q in enumerate(test_questions, 1):
    try:
        res = requests.post(API, json={**q, "show_steps": True}, timeout=180)
        r = res.json()
        l2 = r.get("layer2_result", r.get("final_status", "?"))
        status = r.get("final_status", "?")
        conf = r.get("confidence_score", "?")
        print(f"[{i:2d}/{len(test_questions)}] {q['subject_id']:40s} | L2: {str(l2):15s} | Status: {str(status):10s} | Conf: {conf} | {q['question'][:50]}")
    except Exception as e:
        print(f"[{i:2d}/{len(test_questions)}] ERROR: {e} | {q['question'][:50]}")
    time.sleep(0.5)

print("\nDone! Check the admin dashboard.")
