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
from src.admin import admin_bp

app = Flask(__name__)
CORS(app)

pipeline = TwoLayerPipeline()

# Register admin blueprint
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    show_steps = data.get('show_steps', False)
    force_answer = data.get('force_answer', False)
    history = data.get('history', [])  # NEW: Get conversation history
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Build context from conversation history
    context_prefix = ""
    if history:
        context_prefix = "Previous conversation:\n"
        # Get last 3 Q&A pairs (6 messages max)
        recent_history = history[-6:]
        for msg in recent_history:
            if msg.get('type') == 'user':
                context_prefix += f"User: {msg.get('text', '')}\n"
            elif msg.get('type') == 'bot':
                bot_data = msg.get('data', {})
                answer = bot_data.get('answer', '')
                if answer:
                    # Truncate long answers to 200 chars
                    answer_short = answer[:200] + '...' if len(answer) > 200 else answer
                    context_prefix += f"Assistant: {answer_short}\n"
        context_prefix += "\nCurrent question: "
    
    # Combine context with current question
    full_question = context_prefix + question if context_prefix else question
    
    # Layer 1 & 2: Validate question (use original question for validation)
    validation_result = pipeline.process_question(question)
    
    # Build intermediate steps for review
    steps = {
        'layer1': {
            'name': 'DS Classifier',
            'status': validation_result.get('layer1_result'),
            'latency_ms': validation_result.get('layer1_time_ms', 0),
            'description': 'Checks if question is Data Structures related'
        },
        'layer2': {
            'name': 'Syllabus Checker',
            'status': validation_result.get('layer2_result'),
            'latency_ms': validation_result.get('layer2_time_ms', 0),
            'description': 'Checks if DS topic is in CA3101 syllabus'
        }
    }
    
    if validation_result['final_status'] not in ['VALID', 'WARNING']:
        # Check if OUT_OF_SYLLABUS and user wants answer anyway
        if validation_result['final_status'] == 'OUT_OF_SYLLABUS' and force_answer:
            # User clicked "Answer Anyway" - proceed to Layer 3
            pass  # Continue to Layer 3 below
        else:
            # Return validation result without calling Layer 3
            response = validation_result.copy()
            if show_steps:
                response['intermediate_steps'] = steps
            return jsonify(response)
    
    # Layer 3: Generate answer using RAG with context
    try:
        import time
        layer3_start = time.time()
        rag_result = generate_answer(full_question)  # Use full_question with context
        layer3_time = (time.time() - layer3_start) * 1000
        
        steps['layer3'] = {
            'name': 'RAG Pipeline',
            'status': 'SUCCESS',
            'latency_ms': layer3_time,
            'description': 'FAISS retrieval + Llama 3.1 generation'
        }
        
        response = {
            'status': 'success',
            'question': question,
            'answer': rag_result.get('answer', rag_result) if isinstance(rag_result, dict) else rag_result,
            'final_status': 'VALID',
            'warning': validation_result.get('warning'),  # Include warning if present
            'out_of_syllabus_answered': force_answer  # Flag if this was OUT_OF_SYLLABUS but answered anyway
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

@app.route('/api/chat/direct', methods=['POST'])
def chat_direct():
    """Direct RAG without validation layers - for comparison demo"""
    data = request.json
    question = data.get('question', '')
    history = data.get('history', [])  # NEW: Get conversation history
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Build context from conversation history
    context_prefix = ""
    if history:
        context_prefix = "Previous conversation:\n"
        recent_history = history[-6:]
        for msg in recent_history:
            if msg.get('type') == 'user':
                context_prefix += f"User: {msg.get('text', '')}\n"
            elif msg.get('type') == 'bot':
                if msg.get('comparison'):
                    answer = msg['comparison'].get('answer', '')
                else:
                    answer = msg.get('data', {}).get('answer', '')
                if answer:
                    answer_short = answer[:200] + '...' if len(answer) > 200 else answer
                    context_prefix += f"Assistant: {answer_short}\n"
        context_prefix += "\nCurrent question: "
    
    full_question = context_prefix + question if context_prefix else question
    
    try:
        import time
        start = time.time()
        rag_result = generate_answer(full_question)  # Use full_question with context
        latency = (time.time() - start) * 1000
        
        return jsonify({
            'status': 'success',
            'question': question,
            'answer': rag_result.get('answer', rag_result) if isinstance(rag_result, dict) else rag_result,
            'latency_ms': latency,
            'mode': 'direct'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
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

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        import json
        from datetime import datetime
        
        data = request.json
        feedback_entry = {
            'question': data.get('question'),
            'answer': data.get('answer'),
            'feedback': data.get('feedback'),  # 'helpful' or 'not_helpful'
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_path = base_dir / 'feedback.json'
        
        # Load existing feedback
        if feedback_path.exists():
            with open(feedback_path, 'r') as f:
                feedback_list = json.load(f)
        else:
            feedback_list = []
        
        # Append new feedback
        feedback_list.append(feedback_entry)
        
        # Save back
        with open(feedback_path, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'status': 'success', 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
