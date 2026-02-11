import requests
import json

# Test questions covering all scenarios
test_cases = [
    {
        "name": "VALID - Gets Answer",
        "question": "What is AVL tree rotation?",
        "expected": "VALID"
    },
    {
        "name": "WARNING - Vague Question",
        "question": "Tell me everything about trees",
        "expected": "WARNING"
    },
    {
        "name": "REJECTED - Gibberish",
        "question": "asdfghjkl",
        "expected": "REJECTED"
    },
    {
        "name": "OUT_OF_SYLLABUS - Not DS",
        "question": "What is AWS Lambda?",
        "expected": "OUT_OF_SYLLABUS"
    },
    {
        "name": "OUT_OF_SYLLABUS - DS but not in CA3101",
        "question": "What is a red-black tree?",
        "expected": "OUT_OF_SYLLABUS"
    }
]

API_URL = "http://localhost:5000/api/chat"

print("=" * 80)
print("ACADEMIC DOUBT CLARIFICATION SYSTEM - INTERMEDIATE STEPS DEMO")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"Question: \"{test['question']}\"")
    print(f"Expected: {test['expected']}")
    print()
    
    # Send request with show_steps=True
    response = requests.post(API_URL, json={
        "question": test['question'],
        "show_steps": True
    })
    
    result = response.json()
    
    # Show intermediate steps
    if 'intermediate_steps' in result:
        steps = result['intermediate_steps']
        
        print("INTERMEDIATE STEPS:")
        print("-" * 80)
        
        # Layer 1
        if 'layer1' in steps:
            layer1 = steps['layer1']
            print(f"[Layer 1] {layer1['description']}")
            print(f"  Status: {layer1['status']}")
            print(f"  Latency: {layer1['latency_ms']:.2f}ms")
            print()
        
        # Layer 2
        if 'layer2' in steps:
            layer2 = steps['layer2']
            print(f"[Layer 2] {layer2['description']}")
            print(f"  Status: {layer2['status']}")
            print(f"  Latency: {layer2['latency_ms']:.2f}ms")
            print()
        
        # Layer 3
        if 'layer3' in steps:
            layer3 = steps['layer3']
            print(f"[Layer 3] {layer3['description']}")
            print(f"  Status: {layer3['status']}")
            print(f"  Latency: {layer3['latency_ms']:.2f}ms")
            print()
        
        print("-" * 80)
    
    # Show final result
    print(f"\nFINAL STATUS: {result.get('final_status', result.get('status'))}")
    
    if result.get('final_status') == 'VALID':
        print(f"Answer: {result.get('answer', '')[:150]}...")
    elif 'message' in result:
        print(f"Message: {result['message']}")
    elif 'explanation' in result:
        print(f"Explanation: {result['explanation']}")
    
    if 'total_latency_ms' in result:
        print(f"\nTotal Latency: {result['total_latency_ms']:.2f}ms")
    
    print()

print("=" * 80)
print("DEMO COMPLETE")
print("=" * 80)
