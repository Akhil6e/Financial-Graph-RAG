import streamlit as st
import os
import streamlit.components.v1 as components
from retriever_v3 import HybridRetrieverV3

# Page Configuration
st.set_page_config(page_title="Fin-Graph-RAG 3000", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background: #0e1117;
        color: white;
    }
    h1 {
        color: #4a90e2;
    }
    .stChatInput {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_retriever():
    return HybridRetrieverV3()

try:
    retriever = get_retriever()
except Exception as e:
    st.error(f"Failed to load system: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("🎛️ Controls")
    st.info("System Ready")
    st.markdown("---")
    st.markdown("**Data Sources:**")
    st.markdown("- 📄 Day 8 Smart Vectors")
    st.markdown("- 🕸️ Day 9 Knowledge Graph")
    
    st.markdown("---")
    st.markdown("Created by **Deepam**")

# Main Layout
st.title("🤖 Financial Knowledge Graph RAG")
st.markdown("Ask complex questions about Apple, Microsoft, and Tesla.")

# Tabs for Chat vs Graph
tab1, tab2 = st.tabs(["💬 Chat", "🕸️ Explore Graph"])

with tab1:
    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI Financial Analyst. Ask me anything about the 10-K filings."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input
    if prompt := st.chat_input("Ask a question (e.g., 'Who competes with Apple?')..."):
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Assistant Thinking
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # 1. Retrieval
                vectors = retriever.vector_search(prompt)
                facts = retriever.graph_search(prompt)
                
                # 2. Synthesis
                answer = retriever.generate_answer(prompt, vectors, facts)
                
                st.write(answer)
                
                # Expandable Source View
                with st.expander("🔍 View Sources (Debug)"):
                    st.markdown("### 🕸️ Graph Facts")
                    for f in facts:
                        st.markdown(f"- {f}")
                        
                    st.markdown("### 📄 Text Documents")
                    for idx, doc in enumerate(vectors):
                        st.markdown(f"**Doc {idx+1} ({doc['source']})**")
                        st.caption(doc['text'][:300] + "...")

        # Add to history
        st.session_state.messages.append({"role": "assistant", "content": answer})

with tab2:
    st.header("Interactive Knowledge Graph")
    st.markdown("Visualize the relationships extracted by the LLM.")
    
    # Load HTML file
    graph_html_path = os.path.join(os.path.dirname(__file__), "../Day_09_LLM_Graph/graph_v2.html")
    
    if os.path.exists(graph_html_path):
        with open(graph_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            components.html(html_content, height=800, scrolling=True)
    else:
        st.error("Graph HTML file not found. Please run Day 9 script first.")
