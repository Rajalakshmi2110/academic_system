from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path

base_dir = Path(__file__).parent
os.chdir(base_dir)
sys.path.insert(0, str(base_dir))

from src.layer2_validator.inference import TwoLayerPipeline
from src.layer3_rag.inference import generate_answer

app = Flask(__name__)
CORS(app)

pipeline = TwoLayerPipeline()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    show_steps = data.get('show_steps', False)  # New parameter for review mode
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Layer 1 & 2: Validate question
    validation_result = pipeline.process_question(question)
    
    # Build intermediate steps for review
    steps = {
        'layer1': {
            'status': validation_result.get('layer1_result'),
            'latency_ms': validation_result.get('layer1_time_ms', 0),
            'description': 'Binary classifier (DistilBERT) - DS vs Non-DS'
        },
        'layer2': {
            'status': validation_result.get('layer2_result'),
            'latency_ms': validation_result.get('layer2_time_ms', 0),
            'description': 'Rule-based validator - Quality & Syllabus check'
        }
    }
    
    if validation_result['final_status'] != 'VALID':
        response = validation_result.copy()
        if show_steps:
            response['intermediate_steps'] = steps
        return jsonify(response)
    
    # Layer 3: Generate answer using RAG
    try:
        import time
        layer3_start = time.time()
        answer = generate_answer(question)
        layer3_time = (time.time() - layer3_start) * 1000
        
        steps['layer3'] = {
            'status': 'SUCCESS',
            'latency_ms': layer3_time,
            'description': 'RAG pipeline - FAISS retrieval + Llama 3.1 generation'
        }
        
        response = {
            'status': 'success',
            'question': question,
            'answer': answer,
            'final_status': 'VALID'
        }
        
        if show_steps:
            response['intermediate_steps'] = steps
            response['total_latency_ms'] = validation_result.get('total_latency_ms', 0) + layer3_time
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating answer: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/metrics', methods=['GET'])
def metrics():
    try:
        import json
        metrics_path = base_dir / 'evaluation_results.json'
        with open(metrics_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
