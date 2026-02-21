# Quick Start Guide - Multi-Subject System

## 🚀 Testing the Complete System

### Prerequisites
```bash
# Backend dependencies
pip install torch transformers sentence-transformers faiss-cpu groq PyPDF2

# Frontend dependencies
cd frontend && npm install
```

### 1. Start Backend
```bash
cd backend
export GROQ_API_KEY="your_groq_api_key"
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Test Adding a New Subject

#### Option A: Using the UI (Recommended)
1. Login to Admin Panel (http://localhost:3000/admin)
2. Click "Add Subject" in sidebar
3. Fill form:
   - Name: "Operating Systems"
   - Code: "CS3301"
   - ID: "operating_systems" (auto-filled)
4. Upload syllabus.json:
   ```json
   {
     "course_code": "CS3301",
     "course_name": "OPERATING SYSTEMS",
     "units": [
       {
         "unit_number": 1,
         "title": "INTRODUCTION",
         "topics": [
           "Operating System Concepts",
           "Process Management",
           "Memory Management"
         ]
       }
     ]
   }
   ```
5. Upload documents (PDFs, PPTs)
6. Check "Auto-train model" ✅
7. Click "Create Subject"
8. Wait 5-10 minutes for training to complete

#### Option B: Using API (Testing)
```bash
curl -X POST http://localhost:5000/api/subjects/add \
  -F "name=Operating Systems" \
  -F "code=CS3301" \
  -F "id=operating_systems" \
  -F "syllabus=@syllabus.json" \
  -F "documents=@lecture1.pdf" \
  -F "documents=@lecture2.pdf" \
  -F "auto_train=true"
```

### 4. Monitor Training Progress

Check backend console for:
```
[1/3] Generating 2000+ training samples from syllabus...
  Unit 1: INTRODUCTION (400 questions)
  ...
✓ Training data saved

[2/3] Training Layer 1 model...
Epoch 1/3: Train Acc: 0.9234, Val Acc: 0.9456
Epoch 2/3: Train Acc: 0.9567, Val Acc: 0.9678
Epoch 3/3: Train Acc: 0.9789, Val Acc: 0.9823
✓ Model saved

[3/3] Building vector database...
Processing: lecture1.pdf
Processing: lecture2.pdf
Total chunks: 1234
✓ Vector DB created

✅ Training pipeline completed successfully!
```

### 5. Verify Subject is Ready

#### Check subjects.json
```bash
cat subjects/subjects.json
```

Should show:
```json
{
  "subjects": [
    {
      "id": "operating_systems",
      "name": "Operating Systems",
      "code": "CS3301",
      "active": true,
      "document_count": 2,
      "model_trained": true
    }
  ]
}
```

#### Check folder structure
```bash
ls -R subjects/operating_systems/
```

Should contain:
```
documents/
  lecture1.pdf
  lecture2.pdf
  training_data.json

models/
  layer1_distilbert/
    config.json
    pytorch_model.bin
    tokenizer_config.json

vector_db/
  faiss_index.bin
  chunks.pkl
  metadata.json

syllabus.json
```

### 6. Test Student Interface

1. Go to http://localhost:3000
2. Select "Operating Systems" from dropdown
3. Ask questions:
   - "What is process management?"
   - "Explain memory management"
   - "What topics are covered in Unit 1?"

### 7. Test Admin Features

#### Dashboard
- Select subject from dropdown
- Upload more documents
- Rebuild vector DB
- View stats

#### Metrics
- Select subject
- View Layer 1/2/3 evaluation metrics
- Compare performance across subjects

## 🧪 Manual Testing Checklist

### Subject Creation
- [ ] Create subject with valid syllabus
- [ ] Upload multiple documents (PDF, PPT, Word)
- [ ] Auto-training completes successfully
- [ ] Subject appears in student dropdown
- [ ] Subject appears in admin dropdown

### Training Pipeline
- [ ] Data generation creates 2000+ samples
- [ ] Model training achieves >95% accuracy
- [ ] Vector DB contains all uploaded documents
- [ ] Training runs in background (UI not blocked)

### Student Chat
- [ ] Can select different subjects
- [ ] Questions validated by Layer 1
- [ ] Questions validated by Layer 2 (syllabus)
- [ ] Answers retrieved from correct subject's documents
- [ ] Sources cited correctly

### Admin Operations
- [ ] Upload documents to existing subject
- [ ] Delete documents
- [ ] Download documents
- [ ] Rebuild vector DB
- [ ] View subject-specific stats
- [ ] View subject-specific metrics

## 🐛 Troubleshooting

### Training Fails
```bash
# Check GROQ_API_KEY is set
echo $GROQ_API_KEY

# Check syllabus format
cat subjects/{subject_id}/syllabus.json | python -m json.tool

# Check logs
tail -f backend/training.log
```

### Vector DB Build Fails
```bash
# Check PDFs are readable
python -c "from PyPDF2 import PdfReader; print(PdfReader('file.pdf').pages)"

# Check dependencies
pip install PyPDF2 sentence-transformers faiss-cpu
```

### Model Not Loading
```bash
# Check model files exist
ls subjects/{subject_id}/models/layer1_distilbert/

# Should contain: config.json, pytorch_model.bin, tokenizer files
```

## 📝 Sample Syllabus Template

```json
{
  "course_code": "XXXXX",
  "course_name": "COURSE NAME",
  "units": [
    {
      "unit_number": 1,
      "title": "UNIT TITLE",
      "topics": [
        "Topic 1",
        "Topic 2",
        "Topic 3"
      ]
    },
    {
      "unit_number": 2,
      "title": "UNIT TITLE",
      "topics": [
        "Topic 1",
        "Topic 2"
      ]
    }
  ]
}
```

## 🎯 Expected Results

### After Adding Subject
- Folder created: `subjects/{subject_id}/`
- Files uploaded to `documents/`
- Training data generated: ~2000 samples
- Model trained: >95% validation accuracy
- Vector DB built: All documents indexed
- Subject active: Appears in dropdowns

### Student Experience
- Select subject → Ask question → Get answer with sources
- Layer 1: 99%+ accuracy (valid/invalid classification)
- Layer 2: Syllabus-based validation
- Layer 3: Context-aware answers from documents

### Admin Experience
- Add subjects in <2 minutes (excluding training)
- Training runs in background (5-10 minutes)
- Manage documents per subject
- View metrics per subject

---

**Ready to Test!** 🚀

All features are implemented and pushed to GitHub.
Branch: `multi-subject-support`
