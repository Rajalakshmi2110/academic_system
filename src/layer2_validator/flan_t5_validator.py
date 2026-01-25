import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from pathlib import Path
import re
import json
import time

class FLANT5Validator:
    def __init__(self, model_name='google/flan-t5-base'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        # Load model and tokenizer
        print(f"Loading FLAN-T5 model: {model_name}")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Load prompt template
        prompt_path = Path('src/layer2_validator/prompt_template.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
        
        print(f"FLAN-T5 validator loaded on {self.device}")
    
    def validate_question(self, question):
        """
        Validate a question using FLAN-T5 with academic prompt
        
        Args:
            question (str): The question to validate
            
        Returns:
            dict: Validation result with status, explanation, confidence
        """
        start_time = time.time()
        
        # Format prompt with question
        prompt = self.prompt_template.format(question=question)
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            max_length=512,
            truncation=True
        ).to(self.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=150,
                num_beams=3,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse structured output
        result = self._parse_response(response, question)
        result['inference_time_ms'] = (time.time() - start_time) * 1000
        
        return result
    
    def _parse_response(self, response, question):
        """Parse FLAN-T5 response into structured format"""
        
        # Default values
        status = "WARNING"
        explanation = "Unable to parse model response"
        confidence = 0.5
        
        try:
            # Extract status
            status_match = re.search(r'Status:\s*(VALID|WARNING|REJECTED)', response, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).upper()
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*([^\n]+)', response, re.IGNORECASE)
            if explanation_match:
                explanation = explanation_match.group(1).strip()
            
            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*([0-9]*\.?[0-9]+)', response)
            if confidence_match:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            # Fallback parsing
            if any(word in response.lower() for word in ['valid', 'correct', 'appropriate']):
                status = "VALID"
                confidence = 0.8
            elif any(word in response.lower() for word in ['reject', 'incorrect', 'wrong', 'invalid']):
                status = "REJECTED"
                confidence = 0.8
            else:
                status = "WARNING"
                confidence = 0.6
        
        return {
            'question': question,
            'status': status,
            'explanation': explanation,
            'confidence': confidence,
            'raw_response': response
        }
    
    def batch_validate(self, questions):
        """Validate multiple questions"""
        results = []
        for question in questions:
            result = self.validate_question(question)
            results.append(result)
        return results

def demo_validation():
    """Demo function showing Layer 2 validation"""
    try:
        validator = FLANT5Validator()
        
        # Test questions covering different scenarios
        test_questions = [
            "Explain the TCP three-way handshake process",  # Should be VALID
            "What is the best router for gaming?",  # Should be REJECTED (too vague/commercial)
            "How does CSMA/CD and token ring work together?",  # Should be WARNING (mixed concepts)
            "Describe the 7-layer OSI model",  # Should be VALID
            "TCP uses 5-way handshake for security",  # Should be REJECTED (incorrect)
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
        
        # Batch processing demo
        print("\n=== BATCH PROCESSING ===")
        batch_results = validator.batch_validate(test_questions[:3])
        for result in batch_results:
            print(f"{result['status']}: {result['question'][:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have internet connection for model download")

if __name__ == "__main__":
    demo_validation()