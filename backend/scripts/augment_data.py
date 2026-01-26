import json
import random
from pathlib import Path

def create_augmented_dataset():
    data_path = Path("data/raw/question_dataset_full.json")
    with open(data_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    augmented_data = []
    
    for item in original_data:
        question = item['question']
        label = item['label']
        
        augmented_data.append({
            "id": f"AUG_{len(augmented_data) + 1:04d}",
            "question": question,
            "label": label
        })

        if label == 1:
            if question.lower().startswith(('define', 'describe')):
                # Add casual versions
                core = question.split(' ', 1)[1]
                augmented_data.append({
                    "id": f"AUG_{len(augmented_data) + 1:04d}",
                    "question": f"What is {core}?",
                    "label": label
                })
                augmented_data.append({
                    "id": f"AUG_{len(augmented_data) + 1:04d}",
                    "question": f"Explain {core}",
                    "label": label
                })
            elif question.lower().startswith(('what', 'how', 'explain')):
                # Add formal versions
                if question.endswith('?'):
                    core = question[:-1]
                else:
                    core = question
                
                if core.lower().startswith('what is'):
                    new_core = core[8:]
                elif core.lower().startswith('how do'):
                    new_core = core[7:]
                elif core.lower().startswith('explain'):
                    new_core = core[8:]
                else:
                    new_core = core
                
                augmented_data.append({
                    "id": f"AUG_{len(augmented_data) + 1:04d}",
                    "question": f"Define {new_core}",
                    "label": label
                })
                augmented_data.append({
                    "id": f"AUG_{len(augmented_data) + 1:04d}",
                    "question": f"Describe {new_core}",
                    "label": label
                })
    
    random.shuffle(augmented_data)
    
    output_path = Path("data/processed/augmented_dataset.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(augmented_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(augmented_data)} augmented questions")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    create_augmented_dataset()