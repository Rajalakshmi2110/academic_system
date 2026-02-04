import re
import time

class RuleBasedValidator:
    def __init__(self):
        # Keywords indicating vague/broad questions
        self.vague_patterns = [
            r'\b(everything|anything|all|any)\b',
            r'\b(best|worst|better|good|bad)\b',
            r'\band\b.*\band\b.*\band\b',  # Multiple "and"s
        ]
        
        # Incorrect facts about Data Structures
        self.incorrect_facts = [
            (r'binary search.*o\(n\^2\)', 'Binary search is O(log n), not O(n^2)'),
            (r'binary search.*o\(n\^3\)', 'Binary search is O(log n), not O(n^3)'),
            (r'stack.*\bis\b.*fifo', 'Stack is LIFO (Last In First Out), not FIFO'),
            (r'queue.*\bis\b.*lifo', 'Queue is FIFO (First In First Out), not LIFO'),
            (r'tree.*\bhas\b.*cycle', 'Trees are acyclic by definition'),
            (r'linked list.*o\(1\).*search', 'Linked list search is O(n), not O(1)'),
            (r'bubble sort.*o\(n\s*log\s*n\)', 'Bubble sort is O(n^2), not O(n log n)'),
        ]
        
        # Valid Data Structures topics
        self.valid_topics = [
            'array', 'linked list', 'stack', 'queue', 'tree', 'graph',
            'heap', 'hash', 'sort', 'search', 'binary', 'traversal',
            'bfs', 'dfs', 'recursion', 'complexity', 'big o', 'algorithm',
            'avl', 'bst', 'node', 'pointer', 'insertion', 'deletion',
            'merge sort', 'quick sort', 'bubble sort', 'selection sort',
            'dijkstra', 'spanning tree', 'trie', 'deque', 'priority queue'
        ]
        
        print("Rule-based validator initialized")
    
    def validate_question(self, question):
        start_time = time.time()
        question_lower = question.lower()
        
        # Check for incorrect facts
        for pattern, correction in self.incorrect_facts:
            if re.search(pattern, question_lower):
                return {
                    'question': question,
                    'status': 'REJECTED',
                    'explanation': f'Question contains incorrect information: {correction}',
                    'confidence': 0.95,
                    'inference_time_ms': (time.time() - start_time) * 1000
                }
        
        # Check for vague patterns
        for pattern in self.vague_patterns:
            if re.search(pattern, question_lower):
                return {
                    'question': question,
                    'status': 'WARNING',
                    'explanation': 'Question is too vague or overly broad. Please be more specific.',
                    'confidence': 0.75,
                    'inference_time_ms': (time.time() - start_time) * 1000
                }
        
        # Check if question is too short
        if len(question.split()) < 4:
            return {
                'question': question,
                'status': 'WARNING',
                'explanation': 'Question is too short. Please provide more context.',
                'confidence': 0.70,
                'inference_time_ms': (time.time() - start_time) * 1000
            }
        
        # Check if contains valid data structures topics
        has_valid_topic = any(topic in question_lower for topic in self.valid_topics)
        
        if has_valid_topic:
            return {
                'question': question,
                'status': 'VALID',
                'explanation': 'Question is clear, specific, and factually sound.',
                'confidence': 0.85,
                'inference_time_ms': (time.time() - start_time) * 1000
            }
        else:
            return {
                'question': question,
                'status': 'WARNING',
                'explanation': 'Question may lack specific data structures terminology.',
                'confidence': 0.65,
                'inference_time_ms': (time.time() - start_time) * 1000
            }
    
    def batch_validate(self, questions):
        return [self.validate_question(q) for q in questions]

def demo_validation():
    validator = RuleBasedValidator()
    
    test_questions = [
        "Explain the time complexity of binary search algorithm",
        "What is the best sorting algorithm?",
        "How does stack and queue and tree work together?",
        "Describe BFS and DFS traversal",
        "Stack is FIFO data structure",
        "Binary search has O(n^2) complexity",
        "Compare merge sort and quick sort",
        "Explain everything about data structures and algorithms and complexity"
    ]
    
    print("=== RULE-BASED VALIDATOR DEMO ===\n")
    
    for i, question in enumerate(test_questions, 1):
        result = validator.validate_question(question)
        print(f"Test {i}/{len(test_questions)}:")
        print(f"Question: {question}")
        print(f"Status: {result['status']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Time: {result['inference_time_ms']:.2f} ms")
        print("-" * 60)

if __name__ == "__main__":
    demo_validation()
