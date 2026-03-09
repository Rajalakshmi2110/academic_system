from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Load GROQ_API_KEY from .env

base_dir = Path(__file__).parent
os.chdir(base_dir)
sys.path.insert(0, str(base_dir))

from src.layer2_validator.inference import TwoLayerPipeline
from src.layer3_rag.inference import generate_answer, format_answer
from src.admin import admin_bp
from src.admin.subject_routes import subject_bp
from src.session_manager import SessionManager
from src.metrics_tracker import MetricsTracker
from src.voice.tts_service import generate_voice_explanation

def calculate_confidence(question, context, answer):
    """Calculate confidence score based on context-answer overlap and relevance"""
    if not context or not answer:
        return 0.5
    
    # Normalize text
    answer_lower = answer.lower()
    context_lower = context.lower()
    question_lower = question.lower()
    
    # 1. Context-Answer Word Overlap (50% weight)
    answer_words = set(word for word in answer_lower.split() if len(word) > 3)
    context_words = set(word for word in context_lower.split() if len(word) > 3)
    
    if len(answer_words) == 0:
        overlap_score = 0.5
    else:
        overlap = len(answer_words & context_words) / len(answer_words)
        overlap_score = min(overlap, 1.0)
    
    # 2. Question-Context Relevance (30% weight)
    question_words = set(word for word in question_lower.split() if len(word) > 3)
    if len(question_words) == 0:
        relevance_score = 0.5
    else:
        relevance = len(question_words & context_words) / len(question_words)
        relevance_score = min(relevance, 1.0)
    
    # 3. Answer Length Check (20% weight)
    # Penalize very short or very long answers
    answer_length = len(answer.split())
    if 20 <= answer_length <= 300:
        length_score = 1.0
    elif answer_length < 20:
        length_score = answer_length / 20
    else:
        length_score = max(0.5, 1.0 - (answer_length - 300) / 500)
    
    # Calculate weighted confidence
    confidence = (overlap_score * 0.5) + (relevance_score * 0.3) + (length_score * 0.2)
    
    return round(confidence, 2)


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

pipelines = {}  # Cache pipelines per subject to avoid reloading models

def get_pipeline(subject_id='data_structures'):
    if subject_id not in pipelines:
        pipelines[subject_id] = TwoLayerPipeline(subject_id=subject_id)
    return pipelines[subject_id]

session_manager = SessionManager()
metrics_tracker = MetricsTracker()

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
    subject_id = data.get('subject_id', 'data_structures')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    pipeline = get_pipeline(subject_id)  # Get or create pipeline for this subject
    
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            history = session['history']
    
    follow_up_starters = ['it', 'that', 'this', 'its', 'their', 'them', 'those', 'these']
    follow_up_verbs = ['explain', 'elaborate', 'describe', 'tell', 'give', 'show', 'list', 'compare', 'define']
    q_lower = question.lower().strip()
    q_words = q_lower.split()
    
    is_follow_up = (
        any(q_lower.startswith(kw) for kw in follow_up_starters) or
        (len(q_words) < 6 and any(kw in q_lower for kw in ['more', 'also', 'too', 'types', 'example', 'its', 'their'])) or
        (len(q_words) < 6 and any(q_lower.startswith(v) for v in follow_up_verbs))
    ) and len(history) > 0
    
    # Build context-enriched question for follow-ups
    full_question = question
    if is_follow_up and history:
        last_q = ''
        last_a = ''
        for msg in reversed(history):
            if msg.get('type') == 'bot' and not last_a:
                last_a = (msg.get('data', {}).get('answer', ''))[:200]
            elif msg.get('type') == 'user' and not last_q:
                last_q = msg.get('text', '')
            if last_q and last_a:
                break
        if last_q:
            full_question = f"Regarding '{last_q}': {question}"
    
    # Layer 1 & 2: Validate with enriched question for follow-ups
    validation_result = pipeline.process_question(full_question if is_follow_up else question)
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
    
    # Return early if validation fails (unless user forces answer for OUT_OF_SYLLABUS)
    if validation_result['final_status'] not in ['VALID', 'WARNING']:
        if validation_result['final_status'] == 'OUT_OF_SYLLABUS' and force_answer:
            pass  # User clicked "Answer Anyway" - proceed to Layer 3
        else:
            response = validation_result.copy()
            if show_steps:
                response['intermediate_steps'] = steps
            
            # Track rejected/out-of-syllabus questions too
            metrics_tracker.track_question(subject_id, response)
            
            return jsonify(response)
    
    # Layer 3: Generate answer using RAG (FAISS + Llama 3.1)
    try:
        import time
        layer3_start = time.time()
        # Use context-enriched question for follow-ups, original for new questions
        rag_result = generate_answer(
            full_question if is_follow_up else question,
            subject_id=subject_id,
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
            'context': rag_result.get('context', '') if isinstance(rag_result, dict) else '',
            'confidence_score': calculate_confidence(
                question,
                rag_result.get('context', '') if isinstance(rag_result, dict) else '',
                rag_result.get('answer', rag_result) if isinstance(rag_result, dict) else rag_result
            ),
            'final_status': 'VALID',
            'warning': validation_result.get('warning'),
            'out_of_syllabus_answered': force_answer
        }
        
        response = format_answer(response, output_format)  # Clean HTML entities
        
        if show_steps:
            response['intermediate_steps'] = steps
            response['total_latency_ms'] = validation_result.get('total_latency_ms', 0) + layer3_time
        
        # Save to session for conversation history
        if session_id:
            session_manager.add_message(session_id, {'type': 'user', 'text': question})
            session_manager.add_message(session_id, {'type': 'bot', 'data': response})
        
        # Track metrics
        metrics_tracker.track_question(subject_id, response)
        
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
    subject_id = data.get('subject_id', 'data_structures')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
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
        rag_result = generate_answer(full_question, subject_id=subject_id)
        latency = (time.time() - start) * 1000
        
        return jsonify({
            'status': 'success',
            'question': question,
            'answer': rag_result.get('answer', rag_result) if isinstance(rag_result, dict) else rag_result,
            'sources': rag_result.get('sources', []) if isinstance(rag_result, dict) else [],
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
        subject_id = request.args.get('subject_id', 'data_structures')
        
        # Get usage metrics
        usage_metrics = metrics_tracker.get_metrics(subject_id)
        
        # Get feedback metrics
        feedback_metrics = metrics_tracker.get_feedback_metrics(subject_id)
        
        return jsonify({
            'usage': usage_metrics['usage'],
            'layer1': usage_metrics['layer1'],
            'layer2': usage_metrics['layer2'],
            'feedback': feedback_metrics,
            'daily_stats': usage_metrics['daily_stats'],
            'last_updated': usage_metrics['last_updated']
        })
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
        
        feedback_list.append(feedback_entry)
        
        with open(feedback_path, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'status': 'success', 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/voice/explain', methods=['POST'])
def voice_explain():
    """Generate voice explanation for an answer"""
    from flask import send_file
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '')

    if not question or not answer:
        return jsonify({'error': 'Question and answer are required'}), 400

    try:
        audio_path, explanation = generate_voice_explanation(question, answer)
        return send_file(audio_path, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': f'Voice generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
