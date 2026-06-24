# 📊 Financial Graph RAG: LLM-App for Complex Financial Analysis

## 🚀 Live Demo
**[Run the App on Hugging Face Spaces](https://huggingface.co/spaces/DeepXAi/Finanacial-Graph-RAG)**

---

## 💡 The Problem
Standard RAG (Retrieval-Augmented Generation) applications treat documents as flat text chunks. While they are good at retrieval based on keyword similarity, they **fail** at:
1.  **Connecting disjoint facts:** (e.g., "Company A buys Company B" in one doc, "Company B makes X" in another).
2.  **Structured reasoning:** Understanding definitive relationships like `competitor`, `subsidiary`, or `risk_factor`.
3.  **Complex Q&A:** Answering "How does Apple's supply chain risk compare to Microsoft's?" requires traversing a web of entities, not just finding similar words.

## 🛠️ The Solution: Hybrid Graph RAG
This project implements a **Hybrid Retrieval System** that combines:
1.  **Vector Search (FAISS):** For broad context and semantic similarity.
2.  **Knowledge Graph (NetworkX):** For precise, structured relationship mapping (Entities -> Edges -> Relationships).

By querying both systems simultaneously, the LLM receives a context that is both **broad** (text chunks) and **deep** (relationship graph).

---

## 🏗️ Architecture & Pipeline

### 1. Advanced Data Engineering (ETL)
Instead of naive fixed-size chunking (which breaks sentences), we implemented **Context-Aware Processing**:
-   **Recursive Character Splitting:** Intelligently splits text by paragraphs, then sentences, preserving semantic integrity.
-   **Metadata Enrichment:** Every chunk is tagged with its source (10-K Section), Year, and Company ticker, allowing for precise filtering.

### 2. LLM-Powered Graph Construction
We moved beyond simple keyword matching (NER) to **Semantic Graph Construction**:
-   **Model:** `gpt-4o-mini`
-   **Method:** The LLM reads each text chunk and extracts meaningful triplets: `(Source Entity) --[Relationship]--> (Target Entity)`.
-   **Result:** A NetworkX graph containing thousands of nodes (Companies, Products, Risks, Executives) and edges (Competes With, Acquired, Supply Chain).

### 3. Hybrid Retrieval Engine (The "Brain")
The `HybridRetriever` class performs a dual search:
-   **Vector Search:** Finds the top 5 most similar text chunks using embeddings (`all-MiniLM-L6-v2`).
-   **Graph Search:** Identifies entities in the query (e.g., "Tim Cook") and traverses the Knowledge Graph to find 1-hop and 2-hop neighbors (e.g., "Tim Cook --CEO_OF--> Apple").
-   **Synthesis:** The LLM synthesizes the final answer using *both* the rigorous graph facts and the descriptive text chunks.

---

## 📊 Performance Comparison
We benchmarked this Graph RAG system against a standard Baseline RAG (Vector only).

| Query Type | Standard RAG | **Graph RAG (This Project)** |
| :--- | :--- | :--- |
| **Logic** | Text Similarity Only | **Text + Graph Connections** |
| **Multi-Hop Reasoning** | ❌ Fails to link disjoint facts | ✅ **Links `Risk -> Supplier -> Apple`** |
| **Specificity** | "Apple faces risks..." | **"Apple faces risks from TSMC..."** |
| **Verdict** | Good for summaries | **Superior for Analysis** |

---

## 🐳 Deployment (CI/CD)
The application is containerized using **Docker** to ensure reproducibility.

### Docker Structure
-   **Base Image:** `python:3.10-slim`
-   **Security:** Runs as a non-root user (Standard for Hugging Face Spaces).
-   **Optimization:** Multi-stage build process to keep the image lightweight.

### How to Run Locally with Docker
1.  **Pull the Image:**
    ```bash
    docker pull deepam5708/fin-rag-app:latest
    ```
2.  **Run the Container:**
    ```bash
    docker run -p 7860:7860 -e OPENAI_API_KEY="your-key-here" fin-rag-app
    ```
3.  **Access:** Open `http://localhost:7860` in your browser.

---

## 💻 Tech Stack
-   **LLM:** OpenAI GPT-4o-mini
-   **Graph Database:** NetworkX (Serialized via Pickle)
-   **Vector Database:** FAISS
-   **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
-   **Orchestration:** LangChain Concepts
-   **Backend:** Python
-   **Frontend:** Streamlit
-   **Deployment:** Docker, Hugging Face Spaces

---

