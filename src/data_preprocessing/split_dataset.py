import json
import random
from pathlib import Path

def split_dataset():
    # Set fixed seed for reproducible results
    random.seed(42)
    
    # Define file paths
    raw_data_path = Path("data/raw/question_dataset_full.json")
    processed_dir = Path("data/processed")
    
    # Load the full dataset (handle multiple JSON arrays)
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content by ']\n\n[' to separate multiple arrays
    array_parts = content.split(']\n\n[')
    data = []
    
    for i, part in enumerate(array_parts):
        # Add brackets back to make valid JSON
        if i == 0:
            json_str = part + ']'
        elif i == len(array_parts) - 1:
            json_str = '[' + part
        else:
            json_str = '[' + part + ']'
        
        # Parse and extend data
        data.extend(json.loads(json_str))
    
    # Shuffle the data randomly
    random.shuffle(data)
    
    # Calculate split sizes (70% train, 15% val, 15% test)
    total_size = len(data)
    train_size = int(0.7 * total_size)
    val_size = int(0.15 * total_size)
    
    # Split the data
    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]
    
    # Save split datasets
    with open(processed_dir / "train.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2)
    
    with open(processed_dir / "val.json", 'w', encoding='utf-8') as f:
        json.dump(val_data, f, indent=2)
    
    with open(processed_dir / "test.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    # Print split sizes
    print(f"Dataset split completed:")
    print(f"Training set: {len(train_data)} samples")
    print(f"Validation set: {len(val_data)} samples")
    print(f"Test set: {len(test_data)} samples")
    print(f"Total: {total_size} samples")
    
    # Print label distribution
    train_labels = [item['label'] for item in train_data]
    val_labels = [item['label'] for item in val_data]
    test_labels = [item['label'] for item in test_data]
    
    print(f"\nLabel distribution:")
    print(f"Training - In-syllabus: {train_labels.count(1)}, Out-of-syllabus: {train_labels.count(0)}")
    print(f"Validation - In-syllabus: {val_labels.count(1)}, Out-of-syllabus: {val_labels.count(0)}")
    print(f"Test - In-syllabus: {test_labels.count(1)}, Out-of-syllabus: {test_labels.count(0)}")

if __name__ == "__main__":
    split_dataset()