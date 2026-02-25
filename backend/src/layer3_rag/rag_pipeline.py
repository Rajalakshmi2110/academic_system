import pickle
import faiss
import requests
from sentence_transformers import SentenceTransformer
import json

class RAGPipeline:
    def __init__(self, subject_id='data_structures', vector_db_path=None, ollama_url="http://localhost:11434"):
        from pathlib import Path
        
        self.subject_id = subject_id
        
        # Use provided path or default to subjects/{subject_id}/vector_db
        if vector_db_path:
            self.vector_db_path = vector_db_path
        else:
            base_dir = Path(__file__).parent.parent.parent.parent
            self.vector_db_path = str(base_dir / 'subjects' / subject_id / 'vector_db')
        
        # Load FAISS index and text chunks
        self.index = faiss.read_index(f"{self.vector_db_path}/faiss_index.bin")
        with open(f"{self.vector_db_path}/chunks.pkl", 'rb') as f:
            self.chunks = pickle.load(f)
        
        try:
            with open(f"{self.vector_db_path}/metadata.json", 'r') as f:
                self.metadata = json.load(f)
        except:
            self.metadata = [{"source": f"{subject_id} materials", "page": i} for i in range(len(self.chunks))]
        
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.ollama_url = ollama_url
        self.model_name = "llama3.1:8b"
        
        print(f"RAG Pipeline loaded for {subject_id} with {len(self.chunks)} chunks")
    
    def validate_question(self, question):
        prompt = f"""Is this a valid, clear question? Answer only 'VALID' or 'INVALID: reason'

Question: {question}"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()['response'].strip()
            
            if 'VALID' in result and 'INVALID' not in result:
                return True, "Valid question"
            else:
                return False, result.replace('INVALID:', '').strip()
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def retrieve_context(self, question, top_k=5):
        specific_source = None
        question_lower = question.lower()
        
        # Extract PDF name if mentioned in question
        if '.pdf' in question_lower:
            import re
            match = re.search(r'([\w_]+)\.pdf', question_lower)
            if match:
                specific_source = match.group(1)
        
        # Embed question and search FAISS
        query_embedding = self.embedder.encode([question]).astype('float32')
        
        search_k = top_k * 5 if specific_source else top_k
        distances, indices = self.index.search(query_embedding, search_k)
        
        context_chunks = []
        sources = []
        for idx in indices[0]:
            meta = self.metadata[idx] if idx < len(self.metadata) else {"source": "Unknown", "page": idx}
            
            # Filter by specific source if mentioned
            if specific_source:
                if specific_source.lower() not in meta['source'].lower():
                    continue
            
            chunk_text = self.chunks[idx]
            context_chunks.append(chunk_text)
            sources.append(meta)
            
            if len(context_chunks) >= top_k:
                break
        
        return "\n\n".join(context_chunks), sources
    
    def generate_answer(self, question, context, is_follow_up=False):
        # Detect question type to customize prompt
        doc_keywords = ['.pdf', 'explain unit', 'summarize', 'what is covered in', 'topics in']
        is_doc_summary = any(keyword in question.lower() for keyword in doc_keywords)
        
        code_keywords = ['algorithm', 'pseudocode', 'function', 'procedure', 'implementation']
        needs_code = any(keyword in question.lower() for keyword in code_keywords)
        
        # Create prompt based on question type
        if is_doc_summary:
            prompt = f"""Context: {context}

Question: {question}

The user is asking about the content or topics covered in a document. Based on the context, provide a clear summary of the main topics, concepts, and key points covered.

Answer:"""
        elif is_follow_up:
            prompt = f"""Context: {context}

Question: {question}

The user is asking for MORE details or elaboration. Provide additional information, examples, or deeper explanation that was NOT covered in the previous answer.

Answer:"""
        elif needs_code:
            prompt = f"""Context: {context}

Question: {question}

Using ONLY the context provided above, provide the algorithm/pseudocode in triple backticks (```).

Answer:"""
        else:
            prompt = f"""Context: {context}

Question: {question}

Using ONLY the context provided above, answer the question in 2-3 sentences. Do NOT include code or algorithms.

Answer:"""
        
        # Call Ollama Llama 3.1 for answer generation
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def answer_question(self, question, is_follow_up=False):
        context, sources = self.retrieve_context(question, top_k=10)
        
        answer = self.generate_answer(question, context, is_follow_up)
        
        return {
            "status": "success",
            "context": context,
            "answer": answer,
            "sources": sources
        }
