import json
import faiss
import numpy as np
import os
import networkx as nx
import pickle
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths (Relative to Day_10_Integration folder)
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store_v2.faiss")
VECTOR_METADATA_PATH = os.path.join(BASE_DIR, "vector_metadata_v2.json")
GRAPH_PATH = os.path.join(BASE_DIR, "graph_v2.gpickle")

MODEL_NAME = "all-MiniLM-L6-v2"
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH, override=True)

class HybridRetrieverV3:
    def __init__(self):
        print("🔧 Initializing Hybrid Retriever V3 (Final)...")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
            
        self.client = OpenAI(api_key=self.api_key)
        
        # 1. Load Vector Embeddings (Day 8)
        print("   - Loading Vectors...")
        try:
            self.encoder = SentenceTransformer(MODEL_NAME)
            self.index = faiss.read_index(VECTOR_STORE_PATH)
            with open(VECTOR_METADATA_PATH, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load vectors: {e}")
            raise

        # 2. Load Knowledge Graph (Day 9)
        print("   - Loading Knowledge Graph...")
        try:
            with open(GRAPH_PATH, "rb") as f:
                self.graph = pickle.load(f)
            print(f"     Loaded {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        except Exception as e:
            print(f"❌ Failed to load graph: {e}")
            raise

        print("✅ Hybrid System V3 Ready.")

    def vector_search(self, query, k=5):
        """Standard Semantic Search"""
        q_vec = self.encoder.encode([query])
        D, I = self.index.search(q_vec, k)
        
        results = []
        for idx in I[0]:
            if idx != -1:
                item = self.metadata[idx]
                results.append(item)
        return results

    def graph_search(self, query, hop_limit=1):
        """
        Finds entities in query and returns their direct connections (1-hop neighbors).
        """
        query_lower = query.lower()
        facts = []
        found_entities = []

        # 1. Identify Entities in Query (Simple Case-Insensitive Match)
        # In a real app, use an LLM or SpaCy for NER here.
        # For efficiency, we iterate through nodes (fast enough for 1000 nodes)
        nodes = list(self.graph.nodes())
        
        for node in nodes:
            # Check if node name appears in query (e.g., "Apple" in "Who is CEO of Apple?")
            if str(node).lower() in query_lower:
                found_entities.append(node)
                
        # 2. Traverse Graph
        for entity in found_entities:
            # Get neighbors (outgoing edges)
            if self.graph.has_node(entity):
                # Outgoing edges
                out_edges = self.graph.out_edges(entity, data=True)
                for src, tgt, data in out_edges:
                    rel = data.get("relation", "related_to")
                    facts.append(f"{src} --[{rel}]--> {tgt}")
                    
                # Incoming edges (optional, but good for context)
                in_edges = self.graph.in_edges(entity, data=True)
                for src, tgt, data in in_edges:
                    rel = data.get("relation", "related_to")
                    facts.append(f"{src} --[{rel}]--> {tgt}")
                    
        return list(set(facts)) # Deduplicate

    def generate_answer(self, query, vector_docs, graph_facts):
        """
        Synthesizes an answer using the LLM.
        """
        context_str = ""
        
        # Add Graph Facts (Precision)
        if graph_facts:
            context_str += "--- KNOWLEDGE GRAPH FACTS ---\n"
            for f in graph_facts:
                context_str += f"- {f}\n"

        # Add Vector Docs (Context)
        if vector_docs:
            context_str += "\n--- TEXT DOCUMENTS ---\n"
            for i, d in enumerate(vector_docs):
                source = d.get('source', 'Unknown')
                text = d.get('text', '')
                context_str += f"Doc {i+1} (Source: {source}):\n{text}\n\n"
                
        system_prompt = """You are an expert Financial Analyst. 
        Use the provided context to answer the user's question. 
        
        Strategy:
        1. Use the Knowledge Graph for specific facts (names, roles, relationships).
        2. Use the Text Documents for detailed explanations and context.
        3. Cite your sources implicitly (e.g., "According to the 10-K...").
        4. If you don't know, say so.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {query}\n\nContext:\n{context_str}"}
                ],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ LLM Error: {e}"

if __name__ == "__main__":
    # Quick Test
    bot = HybridRetrieverV3()
    q = "Who is the CEO of Apple?"
    print(f"\n❓ Question: {q}")
    
    vecs = bot.vector_search(q)
    facts = bot.graph_search(q)
    
    print(f"📊 Found {len(vecs)} docs and {len(facts)} graph facts.")
    
    ans = bot.generate_answer(q, vecs, facts)
    print("\n🤖 Answer:")
    print(ans)
