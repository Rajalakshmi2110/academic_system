# Academic Doubt Clarification System - CA3101 Data Structures

A 3-layer intelligent question validation and answering system for CA3101 Data Structures course using ML classification, Groq-based validation, and RAG-based answer generation.

## 🎯 System Overview

This system validates student questions through multiple layers before generating answers, ensuring only relevant, well-formed questions about CA3101 syllabus topics receive responses.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Student Question                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: DS Classifier (DistilBERT)                        │
│  - DS-related vs Non-DS classification                      │
│  - Status: PASS or FAIL                                     │
│  - Accuracy: 99.61% | Latency: ~18ms                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Syllabus Checker (Groq Llama 3.3 70B)             │
│  - Validates: Gibberish, DS relevance, syllabus coverage    │
│  - Status: VALID, WARNING, OUT_OF_SYLLABUS, or REJECTED     │
│  - Latency: ~600-900ms                                      │
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

### Layer 1: DS Classifier
- **Accuracy**: 99.61%
- **Precision**: 100%
- **Recall**: 99.28%
- **F1-Score**: 99.64%
- **Latency**: ~18ms
- **Model**: DistilBERT (fine-tuned)
- **Dataset**: 1,710 questions

### Layer 2: Syllabus Checker
- **Method**: Groq API with Llama 3.3 70B Versatile
- **Latency**: ~600-900ms
- **Coverage**: All CA3101 syllabus topics
- **Fallback**: Rule-based validator (available but not active)

### Layer 3: RAG Generator
- **Vector DB**: 652 chunks from course materials
- **Retrieval**: FAISS with sentence-transformers
- **Generation**: Llama 3.1 8B via Ollama
- **Latency**: 8-10s (optimized from 12s)

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

# Set up Groq API key (free tier: https://console.groq.com/keys)
echo "GROQ_API_KEY=your_key_here" > .env

# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# Pull Llama model
ollama pull llama3.1:8b

# Start Ollama server (in separate terminal)
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
│   │   ├── layer2_validator/   # Groq-based validation
│   │   ├── layer3_rag/         # RAG pipeline
│   │   ├── data_preprocessing/ # Dataset splitting
│   │   └── evaluation/         # End-to-end metrics
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
- Dataset: 1,710 questions (968 in-syllabus, 742 out-of-syllabus)

### Layer 2: Validator
- Primary: Groq API with Llama 3.3 70B (free tier available)
- Fallback: Rule-based validator (85 rules, available but not active)
- Checks: Syllabus coverage, topic relevance, incorrect facts

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
# Layer 1 - DS Classifier
python src/layer1_classifier/evaluate.py

# Layer 2 - Syllabus Checker (requires GROQ_API_KEY)
python -c "from src.layer2_validator.inference import TwoLayerPipeline; p = TwoLayerPipeline(); print(p.process_question('What is AVL tree?'))"

# Layer 3 - RAG Pipeline (requires Ollama running)
python -c "from src.layer3_rag.inference import generate_answer; print(generate_answer('What is AVL tree?'))"
```

## 🎓 Usage Examples

### Valid Questions (Get Answers)
- "What is AVL tree rotation?"
- "Explain binary search tree traversal"
- "How does Dijkstra's algorithm work?"
- "Stack is LIFO right?"
- "Is binary search O(log n)?"
- "Queue uses FIFO?"
- "Array vs linked list?"

### Warning (Incorrect facts but still answered)
- "Stack is FIFO right?" → Layer 3 corrects: "No, Stack is LIFO"
- "Is binary search O(n^2)?" → Layer 3 corrects: "No, it's O(log n)"
- "Queue is LIFO correct?" → Layer 3 corrects: "No, Queue is FIFO"

### Rejected (Not DS-related)
- "What is AWS Lambda?"
- "Explain React framework"
- "asdfghjkl" (gibberish)

### Out-of-Syllabus (DS but not in CA3101)
- "Explain skip lists"
- "What is a Fibonacci heap?"
- "Describe red-black trees"
- "What is dynamic programming?"

## 🔬 Technical Details

### Layer 1 Training
- Dataset: 1,710 questions (968 in-syllabus, 742 out-of-syllabus)
- Split: 70% train (1,197), 15% val (256), 15% test (257)
- Optimizer: AdamW
- Loss: CrossEntropyLoss
- Best Epoch: 3 with 99.22% validation accuracy

### Layer 2 Groq Validator
- Model: Llama 3.3 70B Versatile via Groq API
- Function calling: MCP-style tool to fetch syllabus topics
- Checks: Gibberish, non-DS topics, out-of-syllabus DS topics, incorrect facts
- Fallback: Rule-based validator with 85 rules (available but not active)
- Topics covered: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Heaps, Hashing, Sorting, Searching

### Layer 3 RAG
- Source: Rema Thareja textbook + TV Geetha notes + Unit PDFs
- Total chunks: 652
- Total characters: 1.67M
- Embedding dim: 384

## 🚧 Known Limitations

1. **Latency**: Layer 2 (~600-900ms) + Layer 3 (~8-10s) = ~9-11s total
2. **Scope**: Only CA3101 Data Structures topics
3. **Answer Quality**: Depends on course material coverage
4. **API Dependency**: Layer 2 requires Groq API key (free tier available)
5. **Concurrency**: Limited to 3-4 concurrent users on single machine

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
- Rajalakshmi

## 📧 Contact

For questions or issues, open an issue on GitHub.

---

**Built with:** Python, PyTorch, Transformers, FAISS, Groq, Ollama, React, Flask
