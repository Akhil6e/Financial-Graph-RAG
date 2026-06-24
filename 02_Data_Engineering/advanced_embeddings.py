import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
try:
    from advanced_processing import DocumentProcessor
except ImportError:
    # Fallback if running from root
    from Day_08_Advanced_Data_Engineering.advanced_processing import DocumentProcessor

# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../Day_02/data/processed")
OUTPUT_INDEX_PATH = os.path.join(BASE_DIR, "vector_store_v2.faiss")
OUTPUT_METADATA_PATH = os.path.join(BASE_DIR, "vector_metadata_v2.json")

def generate_advanced_index():
    # 1. Load & Chunk
    print("🚀 Starting Advanced Indexing...")
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    raw_docs = processor.load_documents(DATA_DIR)
    
    all_chunks = []
    chunk_metadata = []

    print("\n✂️  Chunking Documents (Recursive Method)...")
    for doc in raw_docs:
        chunks = processor.recursive_split(doc['text'])
        base_meta = doc['metadata']
        
        for chunk in chunks:
            all_chunks.append(chunk)
            # Store metadata for retrieval later
            chunk_metadata.append({
                "text": chunk,
                "source": base_meta['source'],
                "company": base_meta['company']
            })
            
    print(f"   Total Chunks Generated: {len(all_chunks)}")
    
    # 2. Embed
    print("\n🧠 Generating Embeddings (SentenceTransformer)...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    
    # 3. Create FAISS Index
    print("\n📦 Building FAISS Index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    # 4. Save
    print(f"💾 Saving Index to {OUTPUT_INDEX_PATH}")
    faiss.write_index(index, OUTPUT_INDEX_PATH)
    
    print(f"💾 Saving Metadata to {OUTPUT_METADATA_PATH}")
    with open(OUTPUT_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(chunk_metadata, f, indent=2)
        
    print("\n✅ Day 8 Indexing Complete (v2 Index)!")

if __name__ == "__main__":
    generate_advanced_index()
