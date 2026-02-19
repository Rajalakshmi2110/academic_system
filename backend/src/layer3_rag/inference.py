from .rag_pipeline import RAGPipeline
from pathlib import Path

_pipeline = None

def get_rag_pipeline(vector_db_path=None):
    global _pipeline
    if _pipeline is None:
        if vector_db_path is None:
            # Default to relative path from project root
            project_root = Path(__file__).parent.parent.parent
            vector_db_path = str(project_root / "data" / "vector_db")
        
        _pipeline = RAGPipeline(
            vector_db_path=vector_db_path,
            ollama_url="http://localhost:11434"
        )
    return _pipeline

def generate_answer(question: str, vector_db_path=None, is_follow_up=False) -> str:
    pipeline = get_rag_pipeline(vector_db_path)
    return pipeline.answer_question(question, is_follow_up)
