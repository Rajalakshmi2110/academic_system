import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from pathlib import Path
import time
import json

class Layer1Classifier:
    def __init__(self, model_path='models/layer1_distilbert'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}. Run training first.")
        
        # Load model and tokenizer
        self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Layer 1 classifier loaded on {self.device}")
    
    def predict(self, question, return_confidence=False):
        """
        Predict if a question is relevant to the syllabus.
        
        Args:
            question (str): The question text to classify
            return_confidence (bool): Whether to return confidence scores
            
        Returns:
            dict: Prediction result with label, confidence, and timing
        """
        start_time = time.time()
        
        # Tokenize input
        encoding = self.tokenizer(
            question,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_label = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][predicted_label].item()
        
        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        result = {
            'question': question,
            'label': predicted_label,
            'relevant': predicted_label == 1,
            'confidence': confidence,
            'inference_time_ms': inference_time
        }
        
        if return_confidence:
            result['probabilities'] = {
                'out_of_syllabus': probabilities[0][0].item(),
                'in_syllabus': probabilities[0][1].item()
            }
        
        return result
    
    def batch_predict(self, questions):
        """
        Predict multiple questions at once for better efficiency.
        
        Args:
            questions (list): List of question strings
            
        Returns:
            list: List of prediction results
        """
        start_time = time.time()
        
        # Tokenize all questions
        encodings = self.tokenizer(
            questions,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        
        # Batch inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_labels = torch.argmax(logits, dim=-1)
        
        total_time = (time.time() - start_time) * 1000
        avg_time_per_question = total_time / len(questions)
        
        results = []
        for i, question in enumerate(questions):
            result = {
                'question': question,
                'label': predicted_labels[i].item(),
                'relevant': predicted_labels[i].item() == 1,
                'confidence': probabilities[i][predicted_labels[i]].item(),
                'inference_time_ms': avg_time_per_question
            }
            results.append(result)
        
        return results

def demo_inference():
    """Demo function showing how to use the classifier"""
    try:
        classifier = Layer1Classifier()
        
        # Test questions
        test_questions = [
            "Explain the TCP three-way handshake process",
            "What is the best programming language for web development?",
            "Define CSMA/CD protocol in Ethernet networks",
            "How do I fix my WiFi connection at home?"
        ]
        
        print("=== LAYER 1 INFERENCE DEMO ===")
        
        # Single predictions
        for question in test_questions:
            result = classifier.predict(question, return_confidence=True)
            status = "IN-SYLLABUS" if result['relevant'] else "OUT-OF-SYLLABUS"
            print(f"Q: {question}")
            print(f"Prediction: {status} (confidence: {result['confidence']:.3f})")
            print(f"Inference time: {result['inference_time_ms']:.2f} ms")
            print("-" * 50)
        
        # Batch prediction
        print("\nBatch prediction:")
        batch_results = classifier.batch_predict(test_questions)
        for result in batch_results:
            status = "IN-SYLLABUS" if result['relevant'] else "OUT-OF-SYLLABUS"
            print(f"{status}: {result['question'][:50]}...")
        
        avg_time = sum(r['inference_time_ms'] for r in batch_results) / len(batch_results)
        print(f"Average batch inference time: {avg_time:.2f} ms per question")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run training first: python src/layer1_classifier/train.py")

if __name__ == "__main__":
    demo_inference()