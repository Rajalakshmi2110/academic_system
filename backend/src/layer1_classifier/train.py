import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from pathlib import Path
import time

class QuestionDataset(Dataset):
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
            'labels': torch.tensor(item['label'], dtype=torch.long)
        }

def train_model():
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_name = 'distilbert-base-uncased'
    
    # Load tokenizer and model
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)
    
    train_dataset = QuestionDataset(train_file, tokenizer)
    val_dataset = QuestionDataset('data/processed/val.json', tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)
    
    # Training setup
    optimizer = AdamW(model.parameters(), lr=3e-5)  # Slightly higher LR
    epochs = 8  # Optimal for small dataset
    best_accuracy = 0
    patience = 3
    patience_counter = 0
    
    print(f"Training on {device}")
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    
    train_losses = []
    val_accuracies = []
    
    for epoch in range(epochs):
        # Training
        model.train()
        total_loss = 0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_train_loss = total_loss/len(train_loader)
        train_losses.append(avg_train_loss)
        
        # Validation
        model.eval()
        predictions = []
        true_labels = []
        val_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += outputs.loss.item()
                preds = torch.argmax(outputs.logits, dim=-1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        # Metrics
        accuracy = accuracy_score(true_labels, predictions)
        val_accuracies.append(accuracy)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary')
        
        print(f"Epoch {epoch+1}/{epochs}")
        print(f"Train Loss: {avg_train_loss:.4f}, Val Loss: {val_loss/len(val_loader):.4f}")
        print(f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Early stopping and overfitting detection
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            patience_counter = 0
            model_path = Path('models/layer1_distilbert')
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Fix Windows file locking issue
            try:
                model.save_pretrained(model_path, safe_serialization=False)
                tokenizer.save_pretrained(model_path)
                print(f"Best model saved with accuracy: {best_accuracy:.4f}")
            except Exception as e:
                print(f"Warning: Could not save model - {e}")
                # Save state dict as backup
                torch.save(model.state_dict(), model_path / 'pytorch_model.bin')
        else:
            patience_counter += 1
            
        # Check for overfitting
        if len(train_losses) > 1 and len(val_accuracies) > 1:
            if train_losses[-1] < train_losses[-2] and val_accuracies[-1] < val_accuracies[-2]:
                print("⚠️  Potential overfitting detected: train loss decreasing but val accuracy decreasing")
                
        if patience_counter >= patience:
            print(f"Early stopping triggered after {patience} epochs without improvement")
            break
    
    # Final diagnosis
    print(f"\n=== TRAINING DIAGNOSIS ===")
    print(f"Final train loss: {train_losses[-1]:.4f}")
    print(f"Best validation accuracy: {best_accuracy:.4f}")
    
    if best_accuracy < 0.7:
        print("🔴 UNDERFITTING: Low validation accuracy. Try:")
        print("   - More epochs, lower learning rate, larger model")
    elif len(train_losses) > 2 and train_losses[-1] < 0.1 and best_accuracy < 0.85:
        print("🟡 OVERFITTING: Low train loss but poor validation. Try:")
        print("   - Dropout, regularization, more data, early stopping")
    else:
        print("🟢 GOOD FIT: Model appears to be learning well")
    
    print(f"Training completed. Best accuracy: {best_accuracy:.4f}")
    return best_accuracy >= 0.85

if __name__ == "__main__":
    success = train_model()
    print(f"Target accuracy (≥85%) achieved: {success}")