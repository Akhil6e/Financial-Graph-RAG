import json
import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumes structure: Day_08/.../hybrid_rag_v2.py
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store_v2.faiss")
VECTOR_METADATA_PATH = os.path.join(BASE_DIR, "vector_metadata_v2.json")
RELATIONSHIPS_PATH = os.path.join(BASE_DIR, "../Day_04_Relationships/data/relationships.json")
MODEL_NAME = "all-MiniLM-L6-v2"

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the root .env file
# BASE_DIR is .../Day_08_Advanced_Data_Engineering
ENV_PATH = os.path.join(BASE_DIR, "../.env")
load_dotenv(ENV_PATH, override=True) # Force reload to clear stale cache

class HybridRetriever:
    def __init__(self):
        print("🔧 Initializing Hybrid Retriever V2 (Advanced)...")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️ WARNING: OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=self.api_key)
        
        self.encoder = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(VECTOR_STORE_PATH)
        
        with open(VECTOR_METADATA_PATH, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        with open(RELATIONSHIPS_PATH, "r", encoding="utf-8") as f:
            self.relationships = json.load(f)
            
        # Optimize Graph Lookup
        # Map "Entity Name" -> [List of Related Edges]
        self.graph_index = {}
        for r in self.relationships:
            # Index by Source
            src = r['source'].lower()
            if src not in self.graph_index: self.graph_index[src] = []
            self.graph_index[src].append(r)
            
            # Index by Target
            tgt = r['target'].lower()
            if tgt not in self.graph_index: self.graph_index[tgt] = []
            self.graph_index[tgt].append(r)
            
        print("✅ Hybrid System V2 Ready.")

    def vector_search(self, query, k=3):
        """Standard Semantic Search"""
        # 1. Encode
        q_vec = self.encoder.encode([query])
        
        # 2. Search
        D, I = self.index.search(q_vec, k)
        
        results = []
        for idx in I[0]:
            if idx != -1:
                # V2 Metadata Structure: { "text": "...", "source": "...", "company": "..." }
                item = self.metadata[idx]
                results.append(item['text'])
        return results

    def graph_search(self, query):
        """
        Finds entities in query and returns their direct connections.
        """
        query_lower = query.lower()
        facts = []
        
        # Simple Keyword Matching
        found_entities = []
        for entity_name in self.graph_index.keys():
            if entity_name in query_lower:
                found_entities.append(entity_name)
                
        # Limit to top matches to avoid noise
        for entity in found_entities:
            edges = self.graph_index[entity]
            for e in edges[:5]: # Return max 5 facts per entity
                fact = f"{e['source']} --[{e['relation']}]--> {e['target']}"
                facts.append(fact)
                
        return list(set(facts)) # Deduplicate

    def generate_answer(self, query, vector_docs, graph_facts):
        """
        Synthesizes an answer using the LLM with retrieved context.
        """
        if not self.api_key:
            return "❌ OpenAI API Key not found. Please set it in .env file."

        context_str = ""
        
        # Add Graph Facts (High Precision)
        if graph_facts:
            context_str += "--- KNOWLEDGE GRAPH FACTS ---\n"
            for f in graph_facts:
                context_str += f"- {f}\n"
        
        # Add Vector Docs (High Recall)
        if vector_docs:
            context_str += "\n--- TEXT DOCUMENTS (Advanced chunks) ---\n"
            for i, d in enumerate(vector_docs):
                context_str += f"Doc {i+1}: {d}\n"
                
        system_prompt = """You are a financial analyst assistant. 
        Use the provided context to answer the user's question accurately and professionally.
        If the answer is not in the context, say "I don't have enough information to answer that based on the provided documents."
        Do not hallucinate facts.
        """
        
        user_message = f"Question: {query}\n\nContext:\n{context_str}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Using mini for cost/speed, upgrade to 4o if needed
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ LLM Error: {e}"

if __name__ == "__main__":
    bot = HybridRetriever()
    # Test Run
    test_q = "What are the risk factors for Apple?"
    print(f"\n🧪 Test Query: {test_q}")
    
    # Graph Check
    facts = bot.graph_search(test_q)
    print("Graph Facts:", facts)
    
    # Vector Check
    docs = bot.vector_search(test_q)
    print("Vector Docs:", len(docs))
    for i, doc in enumerate(docs):
        print(f"\n--- Doc {i+1} ---\n{doc[:200]}...")
