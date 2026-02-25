#!/usr/bin/env python3
import pickle
from pathlib import Path

backend_dir = Path(__file__).parent.parent
with open(backend_dir / 'data/vector_db/chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

output_path = backend_dir / 'data/processed/all_chunks.txt'
with open(output_path, 'w') as f:
    f.write(f"Total Chunks: {len(chunks)}\n")
    f.write("="*80 + "\n\n")
    
    for i, chunk in enumerate(chunks):
        f.write(f"CHUNK {i}:\n{chunk}\n\n")
        f.write("="*80 + "\n\n")

print(f"Exported all {len(chunks)} chunks to data/processed/all_chunks.txt")
print(f"📄 File size: ~{sum(len(c) for c in chunks) / 1024 / 1024:.1f} MB")
