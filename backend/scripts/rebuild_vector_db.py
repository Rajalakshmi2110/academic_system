#!/usr/bin/env python3
"""
Rebuild FAISS vector database from PDFs, DOC/DOCX, PPT/PPTX and JSON files
Usage: python rebuild_vector_db.py
"""

import PyPDF2
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not installed. Install with: pip install python-docx")

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    print("⚠️  python-pptx not installed. Install with: pip install python-pptx")

def extract_text_from_pdfs(pdf_dir):
    """Extract text from all PDFs, DOC/DOCX, PPT/PPTX, and JSON files in directory (recursively)"""
    all_text = ""
    metadata = []
    pdf_dir = Path(pdf_dir)
    
    # Load JSON files (recursively)
    for json_file in pdf_dir.rglob('*.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            text = json.dumps(data, indent=2) + "\n\n"
            all_text += text
            metadata.append({"source": json_file.stem, "type": "json", "text": text})
            print(f"✓ {json_file.relative_to(pdf_dir)}")
        except Exception as e:
            print(f"✗ {json_file.name}: {e}")
    
    # Load PDFs (recursively)
    for pdf_file in pdf_dir.rglob('*.pdf'):
        try:
            with open(pdf_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
                        metadata.append({"source": pdf_file.stem, "type": "pdf", "page": page_num, "text": text})
            print(f"✓ {pdf_file.relative_to(pdf_dir)}")
        except Exception as e:
            print(f"✗ {pdf_file.name}: {e}")
    
    # Load DOCX files (recursively)
    if DOCX_AVAILABLE:
        for docx_file in pdf_dir.rglob('*.docx'):
            try:
                doc = Document(docx_file)
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
                all_text += text
                metadata.append({"source": docx_file.stem, "type": "docx", "text": text})
                print(f"✓ {docx_file.relative_to(pdf_dir)}")
            except Exception as e:
                print(f"✗ {docx_file.name}: {e}")
        
        for doc_file in pdf_dir.rglob('*.doc'):
            print(f"⚠️  {doc_file.name}: .doc format not supported, convert to .docx")
    
    # Load PPTX files (recursively)
    if PPTX_AVAILABLE:
        for pptx_file in pdf_dir.rglob('*.pptx'):
            try:
                prs = Presentation(pptx_file)
                text = ""
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            text += shape.text + "\n"
                all_text += text
                metadata.append({"source": pptx_file.stem, "type": "pptx", "text": text})
                print(f"✓ {pptx_file.relative_to(pdf_dir)}")
            except Exception as e:
                print(f"✗ {pptx_file.name}: {e}")
        
        for ppt_file in pdf_dir.rglob('*.ppt'):
            print(f"⚠️  {ppt_file.name}: .ppt format not supported, convert to .pptx")
    
    return all_text, metadata

def chunk_text_with_metadata(text, metadata, size=500, overlap=50):
    """Chunk text with overlap and track source metadata"""
    chunks = []
    chunk_metadata = []
    
    for meta in metadata:
        words = meta['text'].split()
        for i in range(0, len(words), size - overlap):
            chunk = ' '.join(words[i:i + size])
            if len(chunk) > 100:
                chunks.append(chunk)
                chunk_meta = {"source": meta['source'], "type": meta['type']}
                if 'page' in meta:
                    chunk_meta['page'] = meta['page']
                chunk_metadata.append(chunk_meta)
    
    return chunks, chunk_metadata

def build_vector_db(chunks, chunk_metadata, output_dir):
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
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(chunk_metadata, f, indent=2)
    
    print(f"✓ Saved {index.ntotal} vectors to {output_dir}")
    return index.ntotal

if __name__ == "__main__":
    # Configuration - scan entire DS folder
    PDF_DIR = "/Users/rathrajy/learning/project/DS"
    OUTPUT_DIR = Path(__file__).parent.parent / "data" / "vector_db"
    
    print("Extracting text from PDFs, DOC/DOCX, PPT/PPTX, JSON...")
    text, metadata = extract_text_from_pdfs(PDF_DIR)
    print(f"\n✓ Extracted {len(text):,} characters")
    
    print("\nChunking text...")
    chunks, chunk_metadata = chunk_text_with_metadata(text, metadata, size=500, overlap=50)
    print(f"✓ Created {len(chunks)} chunks")
    
    print("\nBuilding vector database...")
    num_vectors = build_vector_db(chunks, chunk_metadata, OUTPUT_DIR)
    
    print(f"\n✅ DONE! Vector DB rebuilt with {num_vectors} vectors")
    print(f"Location: {OUTPUT_DIR}")
    
    # Auto-export all chunks to text file
    print("\nExporting all chunks to text file...")
    try:
        output_file = Path(OUTPUT_DIR) / '../processed/all_chunks.txt'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"Total Chunks: {len(chunks)}\n")
            f.write("="*80 + "\n\n")
            
            for i, chunk in enumerate(chunks):
                f.write(f"CHUNK {i}:\n{chunk}\n\n")
                f.write("="*80 + "\n\n")
        
        print(f"✓ Exported {len(chunks)} chunks to {output_file}")
    except Exception as e:
        print(f"✗ Failed to export chunks: {e}")
