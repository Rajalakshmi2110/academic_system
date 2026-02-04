import json
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DistilBertForSequenceClassification
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
import numpy as np
from pathlib import Path
import time

class QuestionDataset:
    def __init__(self, data_path, tokenizer, max_length=128):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(
            item['question'],
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(item['label'], dtype=torch.long),
            'question': item['question'],
            'id': item['id']
        }

def evaluate_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = Path('models/layer1_distilbert')
    
    if not model_path.exists():
        print("Error: Model not found. Run training first.")
        return False
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    model.to(device)
    model.eval()
    
    test_dataset = QuestionDataset('../../data/processed/test.json', tokenizer)
    test_loader = DataLoader(test_dataset, batch_size=16)
    
    predictions = []
    true_labels = []
    inference_times = []
    
    print(f"Evaluating on {len(test_dataset)} test samples...")
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            start_time = time.time()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            inference_time = (time.time() - start_time) * 1000 / len(input_ids)
            inference_times.append(inference_time)
            
            preds = torch.argmax(outputs.logits, dim=-1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary')
    avg_inference_time = np.mean(inference_times)
    
    print("=== LAYER 1 EVALUATION RESULTS ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"Average inference time: {avg_inference_time:.2f} ms")
    print(f"Target accuracy (>=85%): {'PASS' if accuracy >= 0.85 else 'FAIL'}")
    print(f"Target inference (<100ms): {'PASS' if avg_inference_time < 100 else 'FAIL'}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(true_labels, predictions)
    print(f"True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
    
    print("\nClassification Report:")
    print(classification_report(true_labels, predictions, target_names=['Out-of-syllabus', 'In-syllabus']))
    
    return accuracy >= 0.85 and avg_inference_time < 100

if __name__ == "__main__":
    success = evaluate_model()
    print(f"\nOverall evaluation: {'PASS' if success else 'FAIL'}")