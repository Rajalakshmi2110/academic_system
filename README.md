# Academic Doubt Clarification System - CA3101 Data Structures

A 3-layer intelligent question validation and answering system for CA3101 Data Structures course using ML classification, rule-based validation, and RAG-based answer generation.

## 🎯 System Overview

This system validates student questions through multiple layers before generating answers, ensuring only relevant, well-formed questions about CA3101 syllabus topics receive responses.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Student Question                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Gibberish Detection (Pre-filter)                  │
│  - Detects keyboard mashing, repeated chars                 │
│  - Latency: ~0.08ms                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Binary Classifier (DistilBERT)                    │
│  - DS-related vs Non-DS classification                      │
│  - Accuracy: 99.46% | Latency: 19.89ms                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Rule-Based Validator                              │
│  - Syllabus coverage check (85 rules)                       │
│  - Quality validation (vague, incorrect facts)              │
│  - Latency: 15.31ms                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: RAG Answer Generator                              │
│  - FAISS retrieval (652 chunks, top_k=2)                    │
│  - Llama 3.1 8B generation                                  │
│  - Latency: ~8-10s (optimized)                              │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Performance Metrics

### Layer 1: Binary Classifier
- **Accuracy**: 99.46%
- **Precision**: 98.99%
- **Recall**: 100% (zero false negatives)
- **F1-Score**: 99.49%
- **Latency**: 19.89ms
- **Model**: DistilBERT (fine-tuned)

### Layer 2: Rule-Based Validator
- **Rules**: 85 hardcoded validation rules
- **Latency**: 15.31ms
- **Coverage**: 22 CA3101 syllabus topics

### Layer 3: RAG Generator
- **Vector DB**: 652 chunks from course materials
- **Retrieval**: FAISS with sentence-transformers
- **Generation**: Llama 3.1 8B via Ollama
- **Latency**: 8-10s (optimized from 12s)

### Validation Statuses
- **VALID**: Passes all layers, gets answer
- **WARNING**: In syllabus but poor quality
- **REJECTED**: Gibberish or incorrect facts
- **OUT_OF_SYLLABUS**: Not DS-related OR DS but not in CA3101

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (for Layer 3)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Download pre-trained Layer 1 model (if not included)
python scripts/download_models.py

# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# Pull Llama model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve

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
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
academic_system/
├── backend/
│   ├── data/
│   │   ├── processed/          # Train/val/test splits
│   │   ├── raw/                # Original datasets
│   │   └── vector_db/          # FAISS index + chunks
│   ├── models/
│   │   └── layer1_distilbert/  # Fine-tuned classifier
│   ├── src/
│   │   ├── layer1_classifier/  # DistilBERT training/inference
│   │   ├── layer2_validator/   # Rule-based validation
│   │   ├── layer3_rag/         # RAG pipeline
│   │   └── evaluation/         # Metrics evaluation
│   ├── scripts/
│   │   └── rebuild_vector_db.py
│   └── app.py                  # Flask API
├── frontend/
│   └── src/
│       └── components/
│           └── Student/
│               └── ChatInterface.jsx
└── README.md
```

## 🔧 Configuration

### Layer 1: Classifier
- Model: `distilbert-base-uncased`
- Max length: 128 tokens
- Training: 3 epochs, lr=2e-5

### Layer 2: Validator
- 85 hardcoded rules
- 15 DS topics not in CA3101
- 20 out-of-syllabus keywords
- 30 valid CA3101 topics

### Layer 3: RAG
- Embedder: `sentence-transformers/all-MiniLM-L6-v2`
- Vector DB: FAISS (652 chunks)
- Chunk size: 500 words, overlap: 50
- Retrieval: top_k=2 (optimized)
- LLM: Llama 3.1 8B

## 📚 CA3101 Syllabus Coverage

**Covered Topics:**
- Arrays, Linked Lists, Stacks, Queues
- Binary Trees, AVL Trees, 2-3 Trees, B-Trees
- Graphs (BFS, DFS, Dijkstra, Kruskal, Prim)
- Heaps, Priority Queues
- Hashing (Chaining, Probing)
- Sorting (Bubble, Selection, Merge, Quick)
- Searching (Binary Search)
- Recursion, Complexity Analysis

**Not Covered (Rejected):**
- Skip Lists, Fibonacci Heaps
- Red-Black Trees, Splay Trees
- Suffix Trees, Segment Trees
- Advanced topics beyond CA3101

## 🧪 Testing

### Run Evaluation
```bash
cd backend
python src/evaluation/metrics.py
```

### Test Individual Layers
```bash
# Layer 1
python src/layer1_classifier/evaluate.py

# Layer 2
python src/layer2_validator/inference.py

# Layer 3
python src/layer3_rag/inference.py
```

## 🎓 Usage Examples

### Valid Questions (Get Answers)
- "What is AVL tree rotation?"
- "Explain binary search tree traversal"
- "How does Dijkstra's algorithm work?"

### Warning (In syllabus but poor quality)
- "Explain everything about trees"
- "What is best sorting algorithm?"

### Rejected (Gibberish/Incorrect)
- "asdfghjkl"
- "Binary search is O(n^2)" (incorrect fact)

### Out-of-Syllabus
- "What is AWS Lambda?" (not DS)
- "Explain skip lists" (DS but not in CA3101)

## 🔬 Technical Details

### Layer 1 Training
- Dataset: 1200 questions (600 DS, 600 non-DS)
- Split: 70% train, 15% val, 15% test
- Optimizer: AdamW
- Loss: CrossEntropyLoss

### Layer 2 Rules
- Gibberish patterns: 5 regex rules
- DS not in syllabus: 15 topics
- Out-of-syllabus keywords: 20 items
- Valid topics: 30 CA3101 topics
- Incorrect facts: 8 patterns

### Layer 3 RAG
- Source: Rema Thareja textbook + TV Geetha notes + Unit PDFs
- Total chunks: 652
- Total characters: 1.67M
- Embedding dim: 384

## 🚧 Known Limitations

1. **Latency**: Layer 3 takes 8-10s on CPU (acceptable for academic use)
2. **Scope**: Only CA3101 Data Structures topics
3. **Answer Quality**: Depends on course material coverage
4. **Concurrency**: Limited to 3-4 concurrent users on single machine

## 🔮 Future Improvements

1. **GPU Acceleration**: Deploy on GPU for 1-2s latency
2. **Smaller Model**: Use Phi-3 mini (3.8B) for 2-3s latency
3. **Caching**: Cache common questions
4. **Streaming**: Stream answers token-by-token
5. **Feedback Loop**: Collect user feedback to improve

## 📝 License

Academic project for CA3101 Data Structures course.

## 👥 Contributors

- Rathraj Y

## 📧 Contact

For questions or issues, contact: [your-email]

---

**Built with:** Python, PyTorch, Transformers, FAISS, Ollama, React, Flask
