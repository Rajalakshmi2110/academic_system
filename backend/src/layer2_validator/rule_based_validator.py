import re
import time

class RuleBasedValidator:
    def __init__(self):
        # Out-of-syllabus keywords (safety net for Layer 1 misses)
        self.out_of_syllabus_keywords = [
            'aws', 'azure', 'cloud', 'ec2', 'lambda', 's3', 'athena',
            'kubernetes', 'docker', 'terraform', 'ansible',
            'react', 'angular', 'vue', 'django', 'flask', 'spring',
            'sql', 'database', 'mongodb', 'postgresql', 'mysql',
            'network', 'tcp', 'http', 'api', 'rest', 'graphql'
        ]
        
        # DS topics NOT in CA3101 syllabus
        self.ds_not_in_syllabus = [
            'skip list', 'fibonacci heap', 'red-black tree', 'splay tree',
            'suffix tree', 'segment tree', 'fenwick tree', 'treap',
            'cartesian tree', 'van emde boas', 'fusion tree', 'radix tree',
            'rope data structure', 'bloom filter', 'count-min sketch'
        ]
        

        
        print("Rule-based validator initialized")
    
    def is_gibberish(self, question):
        """Detect gibberish/nonsense text"""
        # Check for excessive repeated characters
        if re.search(r'(.)\1{4,}', question):
            return True
        
        # Check for keyboard mashing patterns
        keyboard_patterns = [
            r'asdf', r'qwer', r'zxcv', r'hjkl', r'uiop',
            r'jkl;', r'fghj', r'cvbn', r'tyui'
        ]
        question_lower = question.lower()
        for pattern in keyboard_patterns:
            if pattern in question_lower and len(question.split()) <= 2:
                return True
        
        # Check if question has mostly non-alphabetic characters
        alpha_chars = sum(c.isalpha() for c in question)
        if len(question) > 0 and alpha_chars / len(question) < 0.5:
            return True
        
        # Check for only punctuation
        if re.match(r'^[^\w\s]+$', question):
            return True
        
        return False
    
    def validate_question(self, question):
        start_time = time.time()
        question_lower = question.lower()
        
        # Check for gibberish first
        if self.is_gibberish(question):
            return {
                'question': question,
                'final_status': 'REJECTED',
                'explanation': 'Question appears to be gibberish or invalid input.',
                'confidence': 0.95,
                'inference_time_ms': (time.time() - start_time) * 1000
            }
        
        # Check for DS topics NOT in CA3101 syllabus
        for ds_topic in self.ds_not_in_syllabus:
            if ds_topic in question_lower:
                return {
                    'question': question,
                    'final_status': 'OUT_OF_SYLLABUS',
                    'explanation': f'"{ds_topic.title()}" is a valid data structure but not covered in CA3101 syllabus.',
                    'suggestion': 'Please ask about topics covered in CA3101: arrays, linked lists, stacks, queues, trees (binary, AVL, 2-3, B-trees), graphs, heaps, hashing, sorting, and searching algorithms.',
                    'confidence': 0.90,
                    'inference_time_ms': (time.time() - start_time) * 1000
                }
        
        # Check for out-of-syllabus keywords
        for keyword in self.out_of_syllabus_keywords:
            if keyword in question_lower:
                return {
                    'question': question,
                    'final_status': 'OUT_OF_SYLLABUS',
                    'explanation': 'This question is not related to the CA3101 Data Structures syllabus.',
                    'suggestion': 'Please ask questions about arrays, linked lists, trees, graphs, sorting, searching, or other data structures topics.',
                    'confidence': 0.90,
                    'inference_time_ms': (time.time() - start_time) * 1000
                }
        
        # If we reach here, question passed all checks
        # Layer 1 already confirmed it's DS-related, so trust that
        return {
            'question': question,
            'status': 'VALID',
            'explanation': 'Question is clear and specific.',
            'confidence': 0.80,
            'inference_time_ms': (time.time() - start_time) * 1000
        }
