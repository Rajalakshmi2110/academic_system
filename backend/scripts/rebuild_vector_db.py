#!/usr/bin/env python3
"""
Rebuild FAISS vector database from PDFs and JSON files
Usage: python rebuild_vector_db.py
"""

import PyPDF2
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

def extract_text_from_pdfs(pdf_dir):
    """Extract text from all PDFs in directory (recursively)"""
    all_text = ""
    pdf_dir = Path(pdf_dir)
    
    # Load JSON files (recursively)
    for json_file in pdf_dir.rglob('*.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            all_text += json.dumps(data, indent=2) + "\n\n"
            print(f"✓ {json_file.relative_to(pdf_dir)}")
        except Exception as e:
            print(f"✗ {json_file.name}: {e}")
    
    # Load PDFs (recursively)
    for pdf_file in pdf_dir.rglob('*.pdf'):
        try:
            with open(pdf_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
            print(f"✓ {pdf_file.relative_to(pdf_dir)}")
        except Exception as e:
            print(f"✗ {pdf_file.name}: {e}")
    
    return all_text

def chunk_text(text, size=500, overlap=50):
    """Chunk text with overlap"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = ' '.join(words[i:i + size])
        if len(chunk) > 100:
            chunks.append(chunk)
    return chunks

def build_vector_db(chunks, output_dir):
    """Build FAISS index from chunks"""
    print("\nBuilding FAISS index...")
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = embedder.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output_dir / 'faiss_index.bin'))
    with open(output_dir / 'chunks.pkl', 'wb') as f:
        pickle.dump(chunks, f)
    
    print(f"✓ Saved {index.ntotal} vectors to {output_dir}")
    return index.ntotal

if __name__ == "__main__":
    # Configuration - scan entire DS folder
    PDF_DIR = "/Users/rathrajy/learning/project/DS"
    OUTPUT_DIR = "backend/data/vector_db"
    
    print("Extracting text from PDFs...")
    text = extract_text_from_pdfs(PDF_DIR)
    print(f"\n✓ Extracted {len(text):,} characters")
    
    print("\nChunking text...")
    chunks = chunk_text(text, size=500, overlap=50)
    print(f"✓ Created {len(chunks)} chunks")
    
    print("\nBuilding vector database...")
    num_vectors = build_vector_db(chunks, OUTPUT_DIR)
    
    print(f"\n✅ DONE! Vector DB rebuilt with {num_vectors} vectors")
    print(f"Location: {OUTPUT_DIR}")
