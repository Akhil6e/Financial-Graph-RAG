import os
import re

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_documents(self, source_dir):
        """
        Loads all .txt files from the source directory.
        Returns a list of dicts: {'text': str, 'metadata': dict}
        """
        documents = []
        if not os.path.exists(source_dir):
            print(f"❌ Error: Directory not found: {source_dir}")
            return []

        print(f"📂 Loading documents from: {source_dir}")
        for filename in os.listdir(source_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(source_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                    
                    # Simple Metadata Extraction from Filename
                    # Expected format: "MSFT_10k_clean.txt" -> Ticker: MSFT
                    ticker = filename.split("_")[0]
                    
                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": filename,
                            "company": ticker,
                            "year": "2024" # Placeholder, typically extracted from text
                        }
                    })
                    print(f"   ✅ Loaded {filename} ({len(text)} chars)")
                except Exception as e:
                    print(f"   ❌ Failed to load {filename}: {e}")
        return documents

    def recursive_split(self, text):
        """
        Splits text recursively by separators: \n\n, \n, ., space.
        Tries to keep chunks under self.chunk_size.
        """
        # 1. Split by Paragraphs (\n\n)
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If adding paragraph exceeds chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                    current_chunk = overlap_text + "\n\n"
                
                # If the paragraph itself is massive (> chunk_size), we must split it further
                if len(para) > self.chunk_size:
                    # 2. Split by Sentences (. )
                    sentences = re.split(r'(?<=[.?!])\s+', para)
                    sub_chunk = ""
                    for sent in sentences:
                        if len(sub_chunk) + len(sent) + 1 > self.chunk_size:
                            if sub_chunk:
                                chunks.append(sub_chunk.strip())
                                # Overlap for sentences
                                ov = sub_chunk[-self.chunk_overlap:] if len(sub_chunk) > self.chunk_overlap else ""
                                sub_chunk = ov + " " + sent
                            else:
                                # Sentence is huge? Forced split (rare but possible)
                                # Just add it for now or slice it
                                chunks.append(sent[:self.chunk_size]) 
                        else:
                            sub_chunk += " " + sent
                    
                    if sub_chunk:
                         current_chunk = sub_chunk # Carry over the remainder
                else:
                    current_chunk += para
            else:
                current_chunk += "\n\n" + para

        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

if __name__ == "__main__":
    # Test Run
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../Day_02/data/processed")
    
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    docs = processor.load_documents(DATA_DIR)
    
    if docs:
        print(f"\n🧩 Testing Splitter on {docs[0]['metadata']['source']}...")
        sample_text = docs[0]['text'][:5000] # Test on first 5000 chars
        chunks = processor.recursive_split(sample_text)
        
        print(f"   Orignal Length: {len(sample_text)}")
        print(f"   Generated {len(chunks)} chunks.")
        for i, c in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i+1} ({len(c)} chars) ---")
            print(c)
            print("-" * 30)
