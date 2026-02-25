#!/usr/bin/env python3
"""
Export vector DB chunks to readable text file for inspection/debugging
Usage: python export_all_chunks.py <subject_id>
"""
import pickle
import sys
from pathlib import Path

def export_chunks(subject_id='data_structures'):
    """Export chunks from vector DB to text file"""
    backend_dir = Path(__file__).parent.parent
    
    # Load chunks from subject's vector DB
    chunks_file = backend_dir / 'subjects' / subject_id / 'vector_db' / 'chunks.pkl'
    
    if not chunks_file.exists():
        print(f"❌ Error: Vector DB not found for '{subject_id}'")
        print(f"   Expected: {chunks_file}")
        print(f"\n   Run training pipeline first or check subject_id")
        return
    
    with open(chunks_file, 'rb') as f:
        chunks = pickle.load(f)
    
    # Export to text file
    output_dir = backend_dir / 'subjects' / subject_id / 'vector_db'
    output_path = output_dir / 'chunks_export.txt'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Subject: {subject_id}\n")
        f.write(f"Total Chunks: {len(chunks)}\n")
        f.write("="*80 + "\n\n")
        
        for i, chunk in enumerate(chunks):
            f.write(f"CHUNK {i}:\n{chunk}\n\n")
            f.write("="*80 + "\n\n")
    
    total_size = sum(len(c) for c in chunks) / 1024 / 1024
    print(f"✅ Exported {len(chunks)} chunks to {output_path}")
    print(f"📄 Total text size: ~{total_size:.1f} MB")
    print(f"\n💡 Use this file to:")
    print(f"   - Debug vector DB retrieval issues")
    print(f"   - Inspect chunk quality")
    print(f"   - Search for specific content: grep 'keyword' {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_all_chunks.py <subject_id>")
        print("Example: python export_all_chunks.py data_structures")
        sys.exit(1)
    
    subject_id = sys.argv[1]
    export_chunks(subject_id)
