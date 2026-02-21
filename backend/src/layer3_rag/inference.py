from .rag_pipeline import RAGPipeline
from pathlib import Path

_pipelines = {}  # Cache pipelines per subject

def get_rag_pipeline(subject_id='data_structures', vector_db_path=None):
    global _pipelines
    
    # Return cached pipeline if exists
    if subject_id in _pipelines:
        return _pipelines[subject_id]
    
    # Create new pipeline for subject
    _pipelines[subject_id] = RAGPipeline(
        subject_id=subject_id,
        vector_db_path=vector_db_path,
        ollama_url="http://localhost:11434"
    )
    return _pipelines[subject_id]

def generate_answer(question: str, subject_id='data_structures', vector_db_path=None, is_follow_up=False) -> str:
    pipeline = get_rag_pipeline(subject_id, vector_db_path)
    return pipeline.answer_question(question, is_follow_up)
