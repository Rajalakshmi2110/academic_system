import json
import random
from pathlib import Path

def split_dataset():
    random.seed(42)
    
    raw_data_path = Path("data/raw/question_dataset_full.json")
    processed_dir = Path("data/processed")
    
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    array_parts = content.split(']\n[')
    data = []
    
    for i, part in enumerate(array_parts):
        if len(array_parts) == 1:
             json_str = part
        elif i == 0:
            json_str = part + ']'
        elif i == len(array_parts) - 1:
            json_str = '[' + part
        else:
            json_str = '[' + part + ']'
        
        json_str = json_str.strip()
        
        if not json_str or json_str in ['[]', '[', ']']:
            continue
            
        try:
            parsed_data = json.loads(json_str)
            data.extend(parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON part {i}: {e}")
            print(f"Problematic JSON: {json_str[:100]}...")
            continue
    
    random.shuffle(data)
    
    total_size = len(data)
    train_size = int(0.7 * total_size)
    val_size = int(0.15 * total_size)
    
    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]
    
    with open(processed_dir / "train.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2)
    
    with open(processed_dir / "val.json", 'w', encoding='utf-8') as f:
        json.dump(val_data, f, indent=2)
    
    with open(processed_dir / "test.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Dataset split completed:")
    print(f"Training set: {len(train_data)} samples")
    print(f"Validation set: {len(val_data)} samples")
    print(f"Test set: {len(test_data)} samples")
    print(f"Total: {total_size} samples")
    
    train_labels = [item['label'] for item in train_data]
    val_labels = [item['label'] for item in val_data]
    test_labels = [item['label'] for item in test_data]
    
    print(f"\nLabel distribution:")
    print(f"Training - In-syllabus: {train_labels.count(1)}, Out-of-syllabus: {train_labels.count(0)}")
    print(f"Validation - In-syllabus: {val_labels.count(1)}, Out-of-syllabus: {val_labels.count(0)}")
    print(f"Test - In-syllabus: {test_labels.count(1)}, Out-of-syllabus: {test_labels.count(0)}")

if __name__ == "__main__":
    split_dataset()