"""
Auto-generate labeled training dataset for Layer 1 classifier
Uses Groq LLM to generate and label questions based on syllabus
"""
import json
import os
from groq import Groq
from pathlib import Path
import time


#MODULE 3
def load_syllabus(syllabus_path):
    """Load syllabus JSON file"""
    with open(syllabus_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_valid_questions(client, topic, subtopics, count=30):
    """Generate valid questions for a topic using LLM"""
    # Limit to 25 questions per call (Groq works better with smaller batches)
    count = min(count, 25)
    
    prompt = f"""Generate exactly {count} diverse questions about the topic: {topic}
Subtopics: {', '.join(subtopics[:5])}

Requirements:
- Mix of conceptual, definition, comparison, and application questions
- Vary complexity (simple to advanced)
- Different question formats (What, Explain, Describe, Compare, How)
- Return ONLY a JSON array of questions, no other text

Example format:
["What is {topic}?", "Explain the concept of...", "Compare X and Y"]
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2000
    )
    
    try:
        questions = json.loads(response.choices[0].message.content)
        return questions if isinstance(questions, list) else []
    except:
        return []

def generate_invalid_questions(client, subject_name, count=20):
    """Generate out-of-scope/invalid questions"""
    # Limit to 20 questions per call
    count = min(count, 20)
    
    prompt = f"""Generate exactly {count} questions that are NOT related to {subject_name}.
Include questions about:
- Other academic subjects (history, chemistry, literature)
- General knowledge (geography, sports, entertainment)
- Programming languages (Python, Java syntax)
- Other CS topics not in {subject_name}
- Gibberish or nonsensical questions

Return ONLY a JSON array of questions, no other text.
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1500
    )
    
    try:
        questions = json.loads(response.choices[0].message.content)
        return questions if isinstance(questions, list) else []
    except:
        return []

def label_question(client, question, syllabus_text):
    """Use LLM to label question as valid (1) or invalid (0)"""
    prompt = f"""Given this syllabus:
{syllabus_text}

Is this question relevant to the syllabus? "{question}"

Answer with ONLY "1" (relevant) or "0" (not relevant). No explanation.
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=5
    )
    
    answer = response.choices[0].message.content.strip()
    return 1 if '1' in answer else 0

def generate_dataset(syllabus_path, output_path, target_count=2000):
    """Generate complete labeled dataset"""
    
    # Initialize Groq client
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        error_msg = "GROQ_API_KEY not found in environment. Please set it in .env file or export it."
        print(f"\nERROR: {error_msg}")
        raise ValueError(error_msg)
    
    client = Groq(api_key=api_key)
    
    # Load syllabus
    syllabus = load_syllabus(syllabus_path)
    subject_name = syllabus.get('course_name', 'Unknown Subject')
    
    # Create syllabus text for labeling
    syllabus_text = f"Course: {subject_name}\n"
    for unit in syllabus.get('units', []):
        syllabus_text += f"\nUnit {unit['unit_number']}: {unit.get('title', unit.get('unit_name', 'Unknown'))}\n"
        syllabus_text += f"Topics: {', '.join(unit['topics'][:10])}\n"
    
    print(f"Generating dataset for: {subject_name}")
    print(f"Target: {target_count} samples")
    
    dataset = []
    question_id = 1
    
    # Calculate distribution
    valid_target = int(target_count * 0.6)  # 60% valid
    invalid_target = target_count - valid_target  # 40% invalid
    
    # Generate valid questions from each unit
    print("\n[1/3] Generating valid questions from syllabus...")
    for unit in syllabus.get('units', []):
        unit_name = unit.get('title', unit.get('unit_name', 'Unknown'))
        topics = unit['topics']
        
        questions_per_unit = valid_target // len(syllabus['units'])
        
        print(f"  Unit {unit['unit_number']}: {unit_name} (target: {questions_per_unit} questions)")
        
        # Generate in batches of 25 (Groq works better with smaller requests)
        unit_questions = []
        batches_needed = (questions_per_unit // 25) + 1
        
        for batch in range(batches_needed):
            if len(unit_questions) >= questions_per_unit:
                break
            
            batch_size = min(25, questions_per_unit - len(unit_questions))
            generated = generate_valid_questions(client, unit_name, topics, batch_size)
            unit_questions.extend(generated)
            time.sleep(12)  # Rate limiting
        
        # Add to dataset
        for q in unit_questions[:questions_per_unit]:  # Limit to target
            dataset.append({
                "id": f"Q{question_id:04d}",
                "question": q,
                "label": 1
            })
            question_id += 1
        
        print(f"    Generated: {len(unit_questions[:questions_per_unit])} questions")
    
    # Generate invalid questions
    print(f"\n[2/3] Generating invalid questions (target: {invalid_target} questions)...")
    invalid_questions = []
    batches_needed = (invalid_target // 20) + 1
    
    for i in range(batches_needed):
        if len(invalid_questions) >= invalid_target:
            break
        
        batch_size = min(20, invalid_target - len(invalid_questions))
        print(f"  Batch {i+1}/{batches_needed}")
        
        invalid_qs = generate_invalid_questions(client, subject_name, batch_size)
        invalid_questions.extend(invalid_qs)
        time.sleep(12)
    
    # Add to dataset
    for q in invalid_questions[:invalid_target]:  # Limit to target
        dataset.append({
            "id": f"Q{question_id:04d}",
            "question": q,
            "label": 0
        })
        question_id += 1
    
    print(f"  Generated: {len(invalid_questions[:invalid_target])} invalid questions")
    
    # Verify labels using LLM (sample check)
    print(f"\n[3/3] Verifying labels (sampling 10%)...")
    sample_size = len(dataset) // 10
    import random
    sample_indices = random.sample(range(len(dataset)), sample_size)
    
    corrections = 0
    for idx in sample_indices:
        item = dataset[idx]
        predicted_label = label_question(client, item['question'], syllabus_text)
        if predicted_label != item['label']:
            dataset[idx]['label'] = predicted_label
            corrections += 1
    
    print(f"  Corrected {corrections} labels")
    
    # Save dataset
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    valid_count = sum(1 for d in dataset if d['label'] == 1)
    invalid_count = len(dataset) - valid_count
    
    print(f"\nDataset generated successfully!")
    print(f"Total samples: {len(dataset)}")
    print(f"Valid (label=1): {valid_count} ({valid_count/len(dataset)*100:.1f}%)")
    print(f"Invalid (label=0): {invalid_count} ({invalid_count/len(dataset)*100:.1f}%)")
    print(f"Saved to: {output_file}")
    print(f"\nSample questions:")
    print(f"  Valid: {dataset[0]['question'][:80]}...")
    print(f"  Invalid: {dataset[valid_count]['question'][:80]}...")
    
    return dataset

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python generate_training_data.py <syllabus_path> <output_path> [target_count]")
        print("Example: python generate_training_data.py ../DS/Syllabus/ca3101_syllabus.json ../data/processed/ds_generated.json 2000")
        sys.exit(1)
    
    syllabus_path = sys.argv[1]
    output_path = sys.argv[2]
    target_count = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    
    generate_dataset(syllabus_path, output_path, target_count)
