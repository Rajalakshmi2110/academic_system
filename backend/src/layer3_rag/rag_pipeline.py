import pickle
import faiss
import requests
from sentence_transformers import SentenceTransformer

class RAGPipeline:
    def __init__(self, vector_db_path, ollama_url="http://localhost:11434"):
        # Load FAISS index and chunks
        self.index = faiss.read_index(f"{vector_db_path}/faiss_index.bin")
        with open(f"{vector_db_path}/chunks.pkl", 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Load embedding model
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Ollama configuration
        self.ollama_url = ollama_url
        self.model_name = "llama3.1:8b"
    
    def retrieve_context(self, question, top_k=2):
        # Embed question
        query_embedding = self.embedder.encode([question]).astype('float32')
        
        # Search FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get relevant chunks
        context_chunks = [self.chunks[idx] for idx in indices[0]]
        return "\n\n".join(context_chunks)
    
    def generate_answer(self, question, context):
        # Create prompt
        prompt = f"""Context: {context}

Question: {question}

Answer in 2 sentences:"""
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def answer_question(self, question):
        context = self.retrieve_context(question, top_k=2)
        answer = self.generate_answer(question, context)
        return answer
