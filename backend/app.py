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
from src.admin.subject_routes import subject_bp
from src.session_manager import SessionManager
from src.output_formatter import OutputFormatter

app = Flask(__name__)
CORS(app)

# Cache pipelines per subject
pipelines = {}

def get_pipeline(subject_id='data_structures'):
    if subject_id not in pipelines:
        pipelines[subject_id] = TwoLayerPipeline(subject_id=subject_id)
    return pipelines[subject_id]

session_manager = SessionManager()
formatter = OutputFormatter()

# Register admin blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(subject_bp, url_prefix='/api/subjects')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    show_steps = data.get('show_steps', False)
    force_answer = data.get('force_answer', False)
    session_id = data.get('session_id')
    output_format = data.get('format', 'json')
    history = data.get('history', [])
    subject_id = data.get('subject_id', 'data_structures')  # NEW: Get subject
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Get pipeline for subject
    pipeline = get_pipeline(subject_id)
    
    # Use session history if session_id provided
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            history = session['history']
    
    # Detect if this is a follow-up question
    follow_up_keywords = ['it', 'that', 'this', 'explain more', 'elaborate', 'what about', 'how about', 'also', 'and']
    is_follow_up = any(question.lower().startswith(kw) for kw in ['it', 'that', 'this', 'what about it', 'how about that']) or \
                   (len(question.split()) < 5 and any(kw in question.lower() for kw in ['more', 'also', 'too']))
    
    # Only use history context if it's a follow-up question
    if is_follow_up and history:
        context_prefix = "Previous conversation:\n"
        recent_history = history[-2:]  # Only last Q&A
        for msg in recent_history:
            if msg.get('type') == 'user':
                context_prefix += f"User: {msg.get('text', '')}\n"
            elif msg.get('type') == 'bot':
                bot_data = msg.get('data', {})
                answer = bot_data.get('answer', '')
                if answer:
                    answer_short = answer[:200] + '...' if len(answer) > 200 else answer
                    context_prefix += f"Assistant: {answer_short}\n"
        context_prefix += "\nCurrent question: "
        full_question = context_prefix + question
    else:
        full_question = question
    
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
    
    # Layer 3: Generate answer using RAG
    try:
        import time
        layer3_start = time.time()
        # Use full_question (with context) only for follow-ups, otherwise use original question
        rag_result = generate_answer(
            full_question if is_follow_up else question,
            subject_id=subject_id,  # NEW: Pass subject_id
            is_follow_up=is_follow_up
        )
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
            'sources': rag_result.get('sources', []) if isinstance(rag_result, dict) else [],
            'final_status': 'VALID',
            'warning': validation_result.get('warning'),
            'out_of_syllabus_answered': force_answer
        }
        
        # Always format the response to clean HTML entities
        response = formatter.format_response(response, output_format)
        
        if show_steps:
            response['intermediate_steps'] = steps
            response['total_latency_ms'] = validation_result.get('total_latency_ms', 0) + layer3_time
        
        # Save to session if session_id provided
        if session_id:
            session_manager.add_message(session_id, {'type': 'user', 'text': question})
            session_manager.add_message(session_id, {'type': 'bot', 'data': response})
        
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
    history = data.get('history', [])
    subject_id = data.get('subject_id', 'data_structures')  # NEW: Get subject
    
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
        rag_result = generate_answer(full_question, subject_id=subject_id)  # NEW: Pass subject_id
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

@app.route('/api/session', methods=['POST'])
def create_session():
    session_id = session_manager.create_session()
    return jsonify({'session_id': session_id})

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    session = session_manager.get_session(session_id)
    if session:
        return jsonify(session)
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    session_manager.clear_session(session_id)
    return jsonify({'status': 'success'})
