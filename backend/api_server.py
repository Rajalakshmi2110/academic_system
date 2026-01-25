import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add academic_system/ to path
sys.path.append(str(Path(__file__).parent.parent))  

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from src.layer2_validator.inference import TwoLayerPipeline

app = Flask(__name__)
CORS(app)

# Set CWD to backend/
if os.getcwd() != str(backend_dir):
    os.chdir(backend_dir)

# Initialize pipeline once at startup
print("Initializing Two-Layer Pipeline...")
pipeline = TwoLayerPipeline()
print("Pipeline ready!")

@app.route('/validate', methods=['POST'])
def validate_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Process through pipeline
        result = pipeline.process_question(question)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'pipeline_ready': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)