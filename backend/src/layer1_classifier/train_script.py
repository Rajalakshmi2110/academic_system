"""
Train Layer 1 DistilBERT classifier from labeled training data
"""
import json
import sys
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
from tqdm import tqdm

class QuestionDataset(Dataset):
    def __init__(self, questions, labels, tokenizer, max_length=128):
        self.questions = questions
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.questions)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.questions[idx],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

def train_model(training_data_path, output_model_path, epochs=2, batch_size=32):
    """Train DistilBERT classifier"""
    
    print(f"Loading training data from {training_data_path}")
    with open(training_data_path, 'r') as f:
        data = json.load(f)
    
    questions = [item['question'] for item in data]
    labels = [item['label'] for item in data]
    
    print(f"Total samples: {len(questions)}")
    print(f"Valid (1): {sum(labels)}, Invalid (0): {len(labels) - sum(labels)}")
    
    # Split data
    train_q, val_q, train_l, val_l = train_test_split(
        questions, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Train: {len(train_q)}, Validation: {len(val_q)}")
    
    # Initialize tokenizer and model
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2
    )
    
    # Create datasets
    train_dataset = QuestionDataset(train_q, train_l, tokenizer)
    val_dataset = QuestionDataset(val_q, val_l, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Training setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=2e-5)
    
    print(f"\nTraining on {device}")
    print(f"Epochs: {epochs}, Batch size: {batch_size}\n")
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in pbar:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            predictions = torch.argmax(outputs.logits, dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
            
            pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{correct/total:.4f}'})
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids, attention_mask=attention_mask)
                predictions = torch.argmax(outputs.logits, dim=1)
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)
        
        train_acc = correct / total
        val_acc = val_correct / val_total
        
        print(f"Epoch {epoch+1}: Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}\n")
    
    # Save model
    output_path = Path(output_model_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    
    # Compute precision, recall, F1, confusion matrix on validation set
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())
    
    precision = precision_score(all_labels, all_preds, average='binary')
    recall = recall_score(all_labels, all_preds, average='binary')
    f1 = f1_score(all_labels, all_preds, average='binary')
    cm = confusion_matrix(all_labels, all_preds).tolist()
    report = classification_report(all_labels, all_preds, target_names=['Out-of-Syllabus', 'In-Syllabus'], output_dict=True)
    
    model_metrics = {
        'accuracy': round(val_acc, 4),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm,
        'classification_report': report,
        'train_samples': len(train_q),
        'val_samples': len(val_q),
        'epochs': epochs
    }
    
    metrics_path = output_path / 'model_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(model_metrics, f, indent=2)
    
    print(f"\nModel saved to {output_path}")
    print(f"Accuracy: {val_acc:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
    print(f"Confusion Matrix: {cm}")
    print(f"Metrics saved to {metrics_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python train_layer1.py <training_data_path> <output_model_path>")
        sys.exit(1)
    
    training_data_path = sys.argv[1]
    output_model_path = sys.argv[2]
    
    train_model(training_data_path, output_model_path)
