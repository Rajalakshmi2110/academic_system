"""
Build FAISS vector database from PDF documents
"""
import sys
import pickle
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def chunk_text(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def build_vector_db(docs_path, output_path):
    """Build FAISS vector database from documents"""
    
    docs_path = Path(docs_path)
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing documents from: {docs_path}")
    
    # Get all PDF files
    pdf_files = list(docs_path.rglob('*.pdf'))
    if not pdf_files:
        print("No PDF files found!")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Extract and chunk text
    all_chunks = []
    metadata = []
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadata.append({
                "source": pdf_file.name,
                "page": i,
                "path": str(pdf_file)
            })
    
    print(f"Total chunks: {len(all_chunks)}")
    
    # Create embeddings
    print("Creating embeddings...")
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = embedder.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # Build FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save everything
    faiss.write_index(index, str(output_path / 'faiss_index.bin'))
    
    with open(output_path / 'chunks.pkl', 'wb') as f:
        pickle.dump(all_chunks, f)
    
    with open(output_path / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Vector database saved to: {output_path}")
    print(f"  - Index: {len(all_chunks)} vectors")
    print(f"  - Dimension: {dimension}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_vector_db.py <docs_path> <output_path>")
        sys.exit(1)
    
    docs_path = sys.argv[1]
    output_path = sys.argv[2]
    
    build_vector_db(docs_path, output_path)
