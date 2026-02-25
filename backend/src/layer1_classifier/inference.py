import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from pathlib import Path
import time

class Layer1Classifier:
    def __init__(self, subject_id='data_structures', model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.subject_id = subject_id
        
        if model_path:
            self.model_path = Path(model_path)
        else:
            base_dir = Path(__file__).parent.parent.parent.parent
            self.model_path = base_dir / 'subjects' / subject_id / 'models' / 'layer1_distilbert'
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train model for {subject_id} first.")
        
        self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Layer 1 classifier loaded for {subject_id} on {self.device}")
    
    def predict(self, question, return_confidence=False):
        start_time = time.time()
        
        encoding = self.tokenizer(
            question,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_label = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][predicted_label].item()
        
        inference_time = (time.time() - start_time) * 1000
        
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
        start_time = time.time()
        
        encodings = self.tokenizer(
            questions,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        
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