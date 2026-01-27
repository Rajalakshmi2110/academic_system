import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from pathlib import Path
import re
import json
import time
from .utils import parse_validation_response

class FLANT5Validator:
    def __init__(self, model_name='google/flan-t5-base'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        print(f"Loading FLAN-T5 model: {model_name}")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        prompt_path = Path('src/layer2_validator/prompt_template.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
        
        print(f"FLAN-T5 validator loaded on {self.device}")
    
    def validate_question(self, question):
        start_time = time.time()
        
        prompt = self.prompt_template.replace("{question}", question)
        
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            max_length=512,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                num_beams=1,
                do_sample=False,
                temperature=0.0,
                early_stopping=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"DEBUG - Raw FLAN-T5 Response: '{response}'")
        
        parsed_result = parse_validation_response(response)
        result = {
            'question': question,
            'status': parsed_result['status'],
            'explanation': parsed_result['explanation'],
            'confidence': parsed_result['confidence'],
            'raw_response': response
        }
        result['inference_time_ms'] = (time.time() - start_time) * 1000
        
        return result
    
    def batch_validate(self, questions):
        results = []
        for question in questions:
            result = self.validate_question(question)
            results.append(result)
        return results

def demo_validation():
    try:
        validator = FLANT5Validator()
        
        test_questions = [
            "Explain the TCP three-way handshake process",
            "What is the best router for gaming?",
            "How does CSMA/CD and token ring work together?",
            "Describe the 7-layer OSI model",
            "TCP uses 5-way handshake for security",
        ]
        
        print("=== LAYER 2 FLAN-T5 VALIDATION DEMO ===")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\nTest {i}/5:")
            print(f"Question: {question}")
            
            result = validator.validate_question(question)
            
            print(f"Status: {result['status']}")
            print(f"Explanation: {result['explanation']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing time: {result['inference_time_ms']:.2f} ms")
            print("-" * 60)
        
        print("\n=== BATCH PROCESSING ===")
        batch_results = validator.batch_validate(test_questions[:3])
        for result in batch_results:
            print(f"{result['status']}: {result['question'][:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have internet connection for model download")

if __name__ == "__main__":
    demo_validation()