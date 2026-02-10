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
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Layer 1 & 2: Validate question
    validation_result = pipeline.process_question(question)
    
    if validation_result['final_status'] != 'VALID':
        return jsonify(validation_result)
    
    # Layer 3: Generate answer using RAG
    try:
        answer = generate_answer(question)
        return jsonify({
            'status': 'success',
            'question': question,
            'answer': answer
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating answer: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
