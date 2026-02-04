# Academic Doubt Clarification System

Two-Layer Intent Classification System for Academic Question Validation - Data Structures

## Project Structure
- `data/` - Dataset files (raw and processed)
- `src/` - Source code modules
- `models/` - Trained model artifacts (auto-generated)
- `notebooks/` - Jupyter notebooks for analysis
- `reports/` - Generated reports and documentation
- `scripts/` - Setup and utility scripts

## Setup Instructions

1. **Clone repository:**
```bash
git clone <repo-url>
cd academic_doubt_clarification_system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download/Train models:**
```bash
python scripts/download_models.py
```
OR manually:
```bash
# Train Layer 1 model
python src/layer1_classifier/train.py

# Layer 2 auto-downloads from Hugging Face
```

4. **Run the system:**
```bash
python src/layer2_validator/inference.py
```

**Notes:**
- Layer 2 (FLAN-T5) auto-downloads from Hugging Face Hub
- Layer 1 (DistilBERT) can be trained using the provided script

## Usage

### Phase 1: Dataset Preprocessing
1. ~~Place dataset in `data/raw/question_dataset_full.json`~~ **DATASET FROZEN**
2. Run preprocessing: `python src/data_preprocessing/split_dataset.py`

### Phase 2: Layer 1 - DistilBERT Classifier
1. Train model: `python src/layer1_classifier/train.py`
2. Evaluate model: `python src/layer1_classifier/evaluate.py`
3. Run inference demo: `python src/layer1_classifier/inference.py`

### Phase 3: Layer 2 - FLAN-T5 Deep Validator
1. Test Layer 2: `python src/layer2_validator/flan_t5_validator.py`
2. Run complete pipeline: `python src/layer2_validator/inference.py`
3. Integration demo: Shows both layers working together

## Dataset Status
**FINAL LABELED DATASET - DO NOT MODIFY**
- File: `data/raw/question_dataset_full.json`
- Status: Frozen for academic experiment
- Entries: 300 questions (Q001-Q300)
- Labels: 150 in-syllabus (1), 150 out-of-syllabus (0)

## Model Performance Targets
- **Layer 1**: Accuracy ≥85%, Inference <100ms