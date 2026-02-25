from .rag_pipeline import RAGPipeline
from pathlib import Path
import re
import html
from typing import Dict, Any

_pipelines = {}  # Cache pipelines per subject

def get_rag_pipeline(subject_id='data_structures', vector_db_path=None):
    global _pipelines
    
    # Return cached pipeline if exists
    if subject_id in _pipelines:
        return _pipelines[subject_id]
    
    _pipelines[subject_id] = RAGPipeline(
        subject_id=subject_id,
        vector_db_path=vector_db_path,
        ollama_url="http://localhost:11434"
    )
    return _pipelines[subject_id]

def format_answer(data: Dict[str, Any], format_type: str = 'json') -> Any:
    """Clean and format answer text"""
    if 'answer' in data and isinstance(data['answer'], str):
        data['answer'] = html.unescape(data['answer'])  # Clean HTML entities
        data['answer'] = re.sub(r'^[=\-]{3,}$', '', data['answer'], flags=re.MULTILINE)  # Remove markdown underlines
        data['answer'] = re.sub(r'\n{3,}', '\n\n', data['answer'])  # Clean extra newlines
    
    if format_type == 'structured':
        data['formatted_answer'] = _structure_answer(data.get('answer', ''))
    return data

def _structure_answer(text: str) -> Dict[str, Any]:
    """Parse answer into structured sections"""
    result = {'sections': []}
    parts = re.split(r'```(?:\w+)?\n?', text)
    
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Code block
            result['sections'].append({'type': 'code', 'content': part.strip()})
        else:  # Text
            if re.search(r'^\s*\d+[\.\)]', part, re.MULTILINE):  # Numbered steps
                steps = [s.strip() for s in re.split(r'\n(?=\d+[\.\)])', part) if s.strip()]
                result['sections'].append({'type': 'steps', 'content': steps})
            elif part.strip():
                result['sections'].append({'type': 'text', 'content': part.strip()})
    
    return result

def generate_answer(question: str, subject_id='data_structures', vector_db_path=None, is_follow_up=False) -> str:
    pipeline = get_rag_pipeline(subject_id, vector_db_path)
    return pipeline.answer_question(question, is_follow_up)
