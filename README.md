# Multi-Subject Academic Doubt Clarification System

A 3-layer intelligent question validation and answering system supporting multiple subjects with automated training pipeline. Built with ML classification, Groq-based validation, and RAG-based answer generation.

## 🎯 System Overview

This system validates student questions through multiple layers before generating answers, ensuring only relevant, well-formed questions receive responses. **Supports unlimited subjects** with automated training pipeline.

### Key Features

✅ **Multi-Subject Support**: Add unlimited subjects (Data Structures, Operating Systems, etc.)
✅ **Automated Training**: Auto-generates 2000+ training samples and trains models
✅ **3-Layer Validation**: DistilBERT → Groq LLM → RAG Pipeline
✅ **Admin Dashboard**: Upload documents, manage subjects, view metrics
✅ **Student Interface**: Subject selector, chat interface, source citations

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Student Question                         │
│              (Subject: Operating Systems)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Subject Classifier (DistilBERT)                   │
│  - Subject-specific model per subject                       │
│  - Valid vs Invalid classification                          │
│  - Accuracy: 99%+ | Latency: ~18ms                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Syllabus Checker (Groq Llama 3.3 70B)             │
│  - Validates against subject-specific syllabus              │
│  - Status: VALID, WARNING, OUT_OF_SYLLABUS, or REJECTED     │
│  - Latency: ~600-900ms                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: RAG Answer Generator                              │
│  - Subject-specific FAISS vector database                   │
│  - Retrieves from subject's uploaded documents              │
│  - Llama 3.1 8B generation                                  │
│  - Latency: ~8-10s                                          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Performance Metrics

### Layer 1: Subject Classifier (Per Subject)
- **Accuracy**: 99%+
- **Model**: DistilBERT (fine-tuned per subject)
- **Training**: Auto-generated 2000+ samples from syllabus
- **Latency**: ~18ms

### Layer 2: Syllabus Checker
- **Method**: Groq API with Llama 3.3 70B
- **Latency**: ~600-900ms
- **Coverage**: Subject-specific syllabus validation

### Layer 3: RAG Generator (Per Subject)
- **Vector DB**: Subject-specific FAISS index
- **Source**: Uploaded PDFs, PPTs, Word docs per subject
- **Generation**: Llama 3.1 8B via Ollama
- **Latency**: 8-10s

### Validation Statuses

**Layer 1 (DS Classifier):**
- **PASS**: Question is DS-related → proceed to Layer 2
- **FAIL**: Not DS-related → REJECTED immediately

**Layer 2 (Syllabus Checker):**
- **VALID**: DS topic in CA3101 syllabus → proceed to Layer 3
- **WARNING**: Contains incorrect facts but in syllabus → proceed to Layer 3 with warning badge
- **OUT_OF_SYLLABUS**: DS topic but not in CA3101 → show "Answer Anyway" button
- **REJECTED**: Gibberish or non-DS topic → stop processing

**Layer 3 (RAG):**
- **SUCCESS**: Answer generated successfully
- **ERROR**: Generation failed

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (for Layer 3)
- Groq API Key (free: https://console.groq.com/keys)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install torch transformers sentence-transformers faiss-cpu groq PyPDF2 flask flask-cors

# Set up Groq API key
export GROQ_API_KEY="your_key_here"

# Install and start Ollama
brew install ollama  # macOS
ollama serve &       # Start in background
ollama pull llama3.1:8b

# Run backend
python app.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Access
- **Student Interface**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **Backend API**: http://localhost:5000

## 📁 Project Structure (Multi-Subject)

```
academic_system/
├── subjects/                          ← All subject data
│   ├── subjects.json                  ← Subject registry
│   ├── data_structures/
│   │   ├── documents/                 ← PDFs, PPTs, Word docs
│   │   │   ├── textbook.pdf
│   │   │   ├── lecture1.pdf
│   │   │   └── training_data.json    ← Auto-generated (2000+ samples)
│   │   ├── models/
│   │   │   └── layer1_distilbert/    ← Trained classifier
│   │   ├── vector_db/                ← FAISS index
│   │   │   ├── faiss_index.bin
│   │   │   ├── chunks.pkl
│   │   │   └── metadata.json
│   │   └── syllabus.json             ← Course structure
│   └── operating_systems/
│       └── (same structure)
├── backend/
│   ├── src/
│   │   ├── subject_manager.py        ← Subject CRUD
│   │   ├── training_pipeline.py      ← Automated training
│   │   ├── layer1_classifier/        ← DistilBERT inference
│   │   ├── layer2_validator/         ← Groq validation
│   │   ├── layer3_rag/               ← RAG pipeline
│   │   └── admin/
│   │       ├── routes.py             ← File management
│   │       └── subject_routes.py     ← Subject management
│   ├── scripts/
│   │   ├── generate_training_data.py ← Auto-generate samples
│   │   ├── train_layer1.py           ← Train DistilBERT
│   │   └── build_vector_db.py        ← Build FAISS index
│   └── app.py                        ← Flask API
├── frontend/
│   └── src/components/
│       ├── Student/
│       │   └── ChatInterface.jsx     ← Subject selector + chat
│       └── Admin/
│           ├── AdminDashboard.jsx    ← File management
│           ├── MetricsPage.jsx       ← Subject metrics
│           └── AddSubjectPage.jsx    ← Add new subject
└── README.md
```

## 🎓 Adding a New Subject

### Via Admin UI (Recommended)

1. **Login to Admin Panel**: http://localhost:3000/admin
2. **Click "Add Subject"** in sidebar
3. **Fill Form**:
   - Subject Name: e.g., "Operating Systems"
   - Course Code: e.g., "OS3101"
   - Subject ID: Auto-filled as "operating_systems"
4. **Upload Syllabus**: `syllabus.json` with course structure
5. **Upload Documents**: PDFs, PPTs, Word files (textbooks, notes)
6. **Enable Auto-Train**: ✅ (recommended)
7. **Click "Create Subject"**

### What Happens Automatically (5-10 minutes)

```
[1/3] Generating 2000+ training samples from syllabus...
  - Uses Groq LLM to create valid/invalid questions
  - Saves to subjects/{subject_id}/documents/training_data.json

[2/3] Training Layer 1 DistilBERT model...
  - Trains on generated data (3 epochs)
  - Saves to subjects/{subject_id}/models/layer1_distilbert/

[3/3] Building FAISS vector database...
  - Processes all uploaded PDFs
  - Creates embeddings and index
  - Saves to subjects/{subject_id}/vector_db/

✅ Subject ready for students!
```

### Syllabus Format

```json
{
  "course_code": "OS3101",
  "course_name": "OPERATING SYSTEMS",
  "units": [
    {
      "unit_number": 1,
      "title": "INTRODUCTION",
      "topics": [
        "Operating System Concepts",
        "System Calls",
        "Process Management"
      ]
    }
  ]
}
```

## 🎯 Usage Examples

### Student Workflow

1. **Select Subject**: Choose from dropdown (e.g., "Data Structures")
2. **Ask Question**: "What is AVL tree rotation?"
3. **Get Answer**: With source citations from uploaded documents

### Admin Workflow

1. **Dashboard**: Upload/delete documents, rebuild vector DB
2. **Metrics**: View Layer 1/2/3 performance per subject
3. **Add Subject**: Upload syllabus + documents, auto-train model

## 🔬 Technical Details

### Automated Training Pipeline
- **Data Generation**: Groq Llama 3.3 70B generates 2000+ samples
- **Model Training**: DistilBERT (3 epochs, ~5 minutes)
- **Vector DB**: FAISS with all-MiniLM-L6-v2 embeddings
- **Execution**: Background thread (non-blocking)

### Multi-Subject Architecture
- **Isolation**: Each subject has own models, data, vector DB
- **Scalability**: Add unlimited subjects
- **Caching**: Pipeline instances cached per subject
- **Path Resolution**: Absolute paths from backend to project root

## 🚧 Known Limitations

1. **Training Time**: 5-10 minutes per subject (runs in background)
2. **Latency**: Layer 2 (~600-900ms) + Layer 3 (~8-10s) = ~9-11s total
3. **API Dependency**: Requires Groq API key (free tier available)
4. **Concurrency**: Limited to 3-4 concurrent users per subject

## 🔮 Future Improvements

1. **Training Progress UI**: Real-time status in admin panel
2. **GPU Acceleration**: Deploy on GPU for faster inference
3. **Streaming Answers**: Token-by-token generation
4. **Subject Templates**: Pre-configured syllabus templates
5. **Bulk Import**: Upload multiple subjects at once

## 📝 License

Academic project for multi-subject doubt clarification system.

## 👥 Contributors

- Rathraj Y
- Rajalakshmi

## 📧 Contact

For questions or issues, open an issue on GitHub.

---

**Built with:** Python, PyTorch, Transformers, FAISS, Groq, Ollama, React, Flask, Material-UI

**Branch:** `multi-subject-support`
