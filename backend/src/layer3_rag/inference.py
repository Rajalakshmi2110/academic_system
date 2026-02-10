from .rag_pipeline import RAGPipeline

_pipeline = None

def get_rag_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline(
            vector_db_path="data/vector_db",
            ollama_url="http://localhost:11434"
        )
    return _pipeline

def generate_answer(question: str) -> str:
    pipeline = get_rag_pipeline()
    return pipeline.answer_question(question)
