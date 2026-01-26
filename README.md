# Academic Doubt Clarification System

Two-Layer AI System for CA3104 Computer Networks Question Validation

## System Overview
Production-ready academic question validator with web interface:
- **Layer 1**: DistilBERT classifier for syllabus relevance (99.7% accuracy)
- **Layer 2**: FLAN-T5 validator for academic quality assessment
- **Web UI**: React frontend with real-time validation
- **API**: Flask REST API with detailed intermediate steps

## Quick Start

1. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python api_server.py
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

3. **Access System:**
- Web UI: http://localhost:3000
- API: http://localhost:5000

## Project Structure
```
academic_system/
├── backend/
│   ├── api_server.py          # Flask API server
│   ├── src/
│   │   ├── layer1_classifier/ # DistilBERT syllabus classifier
│   │   └── layer2_validator/  # FLAN-T5 academic validator
│   ├── models/                # Trained model files
│   ├── data/                  # Datasets (1,686 augmented questions)
│   └── scripts/               # Utility scripts
└── frontend/
    ├── src/
    │   ├── App.tsx           # React main component
    │   └── App.css           # Professional UI styling
    └── public/               # Static assets
```

## Model Performance
- **Layer 1 Accuracy**: 99.7% (format bias eliminated)
- **Layer 1 Speed**: ~110ms average inference
- **Layer 2 Speed**: ~650ms average validation
- **Total Processing**: <1 second end-to-end
- **Format Independence**: All question styles supported

## Dataset Status
**PRODUCTION DATASET**
- Original: 1,090 questions
- Augmented: 1,686 questions (format bias fixed)
- Training: 1,348 questions
- Validation: 338 questions
- Labels: Networking (1), Non-networking (0)

## API Endpoints

### POST /validate
Validate a question through the two-layer pipeline.

**Request:**
```json
{
  "question": "Define TCP three-way handshake"
}
```

**Response:**
```json
{
  "question": "Define TCP three-way handshake",
  "final_status": "VALID",
  "layer1_result": "IN_SYLLABUS",
  "layer2_result": "VALID",
  "explanation": "The question is academically valid and well-formed.",
  "confidence": 0.85,
  "total_latency_ms": 737.34,
  "intermediate_steps": [
    {
      "step": 1,
      "name": "Layer 1 - DistilBERT Classifier",
      "description": "Checking syllabus relevance",
      "status": "IN_SYLLABUS",
      "time_ms": 94.09,
      "output": {
        "confidence": 0.9994,
        "probabilities": {"in_syllabus": 0.9994, "out_of_syllabus": 0.0006}
      }
    },
    {
      "step": 2,
      "name": "Layer 2 - FLAN-T5 Validator",
      "description": "Academic quality validation",
      "status": "VALID",
      "time_ms": 643.26,
      "output": {
        "status": "VALID",
        "explanation": "The question is academically valid and well-formed.",
        "confidence": 0.85
      }
    }
  ]
}
```

### GET /health
Health check endpoint.

## Validation Results
- **VALID**: Academically sound, syllabus-relevant question
- **WARNING**: Too vague or broad, needs clarification
- **REJECTED**: Contains technical errors
- **OUT_OF_SYLLABUS**: Not related to Computer Networks

## Features
- ✅ **Format Bias Eliminated**: All question formats work correctly
- ✅ **Real-time Validation**: Instant feedback through web interface
- ✅ **Detailed Analytics**: Step-by-step processing transparency
- ✅ **Professional UI**: Clean, academic-themed design
- ✅ **Production Ready**: Robust error handling and performance
- ✅ **Academic Evaluation**: Complete intermediate outputs for marking

## Technology Stack
- **Backend**: Python, Flask, PyTorch, Transformers
- **Frontend**: React, TypeScript, CSS3
- **AI Models**: DistilBERT, FLAN-T5
- **Data**: 1,686 augmented questions with balanced formats

## Course Integration
**CA3104 Computer Networks Syllabus Coverage:**
- Network protocols and architectures
- OSI/TCP-IP model layers
- Routing algorithms (OSPF, BGP)
- IP addressing and subnetting
- Transport protocols (TCP/UDP)
- Application protocols (DNS, HTTP, SNMP)
- Network management and SDN
- Ethernet and wireless technologies