"""
Evaluate existing Layer 1 models and generate model_metrics.json
"""
import json, sys, torch
from pathlib import Path
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

def evaluate_model(model_path, training_data_path):
    model_path = Path(model_path)
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    with open(training_data_path, 'r') as f:
        data = json.load(f)

    questions = [item['question'] for item in data]
    labels = [item['label'] for item in data]
    _, val_q, _, val_l = train_test_split(questions, labels, test_size=0.2, random_state=42, stratify=labels)

    all_preds = []
    for q in val_q:
        enc = tokenizer(q, truncation=True, padding='max_length', max_length=128, return_tensors='pt')
        with torch.no_grad():
            out = model(enc['input_ids'].to(device), attention_mask=enc['attention_mask'].to(device))
        all_preds.append(torch.argmax(out.logits, dim=1).item())

    acc = sum(p == l for p, l in zip(all_preds, val_l)) / len(val_l)
    precision = precision_score(val_l, all_preds, average='binary')
    recall = recall_score(val_l, all_preds, average='binary')
    f1 = f1_score(val_l, all_preds, average='binary')
    cm = confusion_matrix(val_l, all_preds).tolist()
    report = classification_report(val_l, all_preds, target_names=['Out-of-Syllabus', 'In-Syllabus'], output_dict=True)

    metrics = {
        'accuracy': round(acc, 4),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm,
        'classification_report': report,
        'val_samples': len(val_l)
    }

    out_path = model_path / 'model_metrics.json'
    with open(out_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Accuracy: {acc:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
    print(f"Confusion Matrix: {cm}")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python evaluate_model.py <model_path> <training_data_path>")
        sys.exit(1)
    evaluate_model(sys.argv[1], sys.argv[2])
