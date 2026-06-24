import json
import os
import networkx as nx
import pickle
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
from pyvis.network import Network

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Input: Day 8 Smart Chunks
INPUT_METADATA_PATH = os.path.join(BASE_DIR, "../Day_08_Advanced_Data_Engineering/vector_metadata_v2.json")
# Output: Day 9 Graph
OUTPUT_GRAPH_PATH = os.path.join(BASE_DIR, "graph_v2.gpickle")
OUTPUT_RELATIONS_PATH = os.path.join(BASE_DIR, "relationships_v2.json")

# Load Environment
ENV_PATH = os.path.join(BASE_DIR, "../.env")
load_dotenv(ENV_PATH, override=True)

class LLMGraphBuilder:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY not found!")
        
        self.client = OpenAI(api_key=self.api_key)
        self.graph = nx.DiGraph()
        
        # Load Data
        with open(INPUT_METADATA_PATH, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
            
        print(f"✅ Loaded {len(self.chunks)} chunks from Day 8.")

    def extract_relationships(self, text, source_doc):
        """
        Uses GPT-4o-mini to extract structured relationships.
        """
        system_prompt = """
        You are an expert Data Scientist. Extract meaningful relationships from the text.
        Return a JSON object with a key "relationships" containing a list of objects.
        Each object must have:
        - "source": Entity 1 (Name)
        - "target": Entity 2 (Name)
        - "relation": UPPERCASE_VERB (e.g., COMPETES_WITH, CEO_OF, ACQUIRED, REVENUE_OF, LOCATED_IN)
        
        Rules:
        1. Ignore generic terms like "Company", "Registrant", "We".
        2. Use specific names (e.g., "Apple Inc.", "Tim Cook").
        3. If no relationships are found, return empty list.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Text: {text}"}
                ],
                response_format={ "type": "json_object" },
                temperature=0
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return data.get("relationships", [])
        except Exception as e:
            print(f"❌ Error extracting: {e}")
            return []

    def build_graph(self, limit=None, start_index=0):
        """
        Process chunks and build the graph.
        limit: (int) Process only N chunks for testing.
        start_index: (int) Skip the first N chunks (useful to skip TOC/Legal).
        """
        end_index = start_index + limit if limit else len(self.chunks)
        print(f"🚀 Starting Extraction (Chunks {start_index} to {end_index})...")
        
        all_relations = []
        chunks_to_process = self.chunks[start_index:end_index]
        
        for i, chunk in enumerate(tqdm(chunks_to_process)):
            text = chunk['text']
            # Heuristic: Skip very short chunks
            if len(text) < 100: continue
            
            rels = self.extract_relationships(text, chunk['source'])
            
            for r in rels:
                src = r['source']
                tgt = r['target']
                rel = r['relation']
                
                # Add to NetworkX
                self.graph.add_edge(src, tgt, relation=rel)
                
                # Add to List for JSON backup
                all_relations.append(r)
                
        print(f"\n✅ Extraction Complete!")
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")
        
        # Save
        print(f"💾 Saving Graph to {OUTPUT_GRAPH_PATH}")
        # NetworkX 3.0+ removed write_gpickle, use standard pickle
        with open(OUTPUT_GRAPH_PATH, "wb") as f:
            pickle.dump(self.graph, f)
        
        print(f"💾 Saving Relations to {OUTPUT_RELATIONS_PATH}")
        with open(OUTPUT_RELATIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(all_relations, f, indent=2)

    def visualize_graph(self):
        """
        Creates an interactive HTML visualization of the graph.
        """
        print(f"🎨 Generating Graph Visualization...")
        net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white")
        
        # Convert NetworkX graph to PyVis
        # PyVis needs string IDs
        for node in self.graph.nodes():
            net.add_node(str(node), label=str(node), title=str(node), color="#4a90e2")
            
        for source, target, data in self.graph.edges(data=True):
            label = data.get("relation", "")
            net.add_edge(str(source), str(target), title=label, label=label)
            
        # Physics options for better layout
        net.barnes_hut()
        
        output_path = os.path.join(BASE_DIR, "graph_v2.html")
        net.show(output_path)
        print(f"✨ Visualization saved to: {output_path}")

if __name__ == "__main__":
    builder = LLMGraphBuilder()
    
    # 🚨 FULL RUN: Processing ALL chunks
    print("🚦 FULL PRODUCTION RUN: Processing all 1143 chunks. This may take ~20 mins.")
    builder.build_graph(limit=None) 
    
    builder.visualize_graph()
