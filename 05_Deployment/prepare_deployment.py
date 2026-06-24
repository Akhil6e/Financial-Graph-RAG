import os
import shutil

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(BASE_DIR, "deployment_package")
APP_DIR = os.path.join(DEPLOY_DIR, "app")

# Source Paths (Relative to Day_12_Deployment)
ROOT_DIR = os.path.dirname(BASE_DIR)
DAY_08_DIR = os.path.join(ROOT_DIR, "Day_08_Advanced_Data_Engineering")
DAY_09_DIR = os.path.join(ROOT_DIR, "Day_09_LLM_Graph")
DAY_10_DIR = os.path.join(ROOT_DIR, "Day_10_Integration")

def setup_directories():
    if os.path.exists(DEPLOY_DIR):
        shutil.rmtree(DEPLOY_DIR)
    os.makedirs(APP_DIR)
    print(f"✅ Created deployment directory: {APP_DIR}")

def copy_data_files():
    # 1. Vectors
    shutil.copy(os.path.join(DAY_08_DIR, "vector_store_v2.faiss"), APP_DIR)
    shutil.copy(os.path.join(DAY_08_DIR, "vector_metadata_v2.json"), APP_DIR)
    
    # 2. Graph
    shutil.copy(os.path.join(DAY_09_DIR, "graph_v2.gpickle"), APP_DIR)
    shutil.copy(os.path.join(DAY_09_DIR, "graph_v2.html"), APP_DIR)
    print("✅ Copied all data files (Vectors + Graph).")

def process_python_files():
    # 1. retriever_v3.py
    with open(os.path.join(DAY_10_DIR, "retriever_v3.py"), "r", encoding="utf-8") as f:
        content = f.read()
    
    # REWRITE PATHS: Remove "../Day_XX/..." and look in current dir
    content = content.replace('../Day_08_Advanced_Data_Engineering/vector_store_v2.faiss', 'vector_store_v2.faiss')
    content = content.replace('../Day_08_Advanced_Data_Engineering/vector_metadata_v2.json', 'vector_metadata_v2.json')
    content = content.replace('../Day_09_LLM_Graph/graph_v2.gpickle', 'graph_v2.gpickle')
    content = content.replace('../.env', '.env') # We won't use .env in Docker, but good fallback
    
    with open(os.path.join(APP_DIR, "retriever_v3.py"), "w", encoding="utf-8") as f:
        f.write(content)
        
    # 2. final_app.py -> app.py
    with open(os.path.join(DAY_10_DIR, "final_app.py"), "r", encoding="utf-8") as f:
        content = f.read()
        
    # REWRITE PATHS
    content = content.replace('../Day_09_LLM_Graph/graph_v2.html', 'graph_v2.html')
    
    with open(os.path.join(APP_DIR, "app.py"), "w", encoding="utf-8") as f:
        f.write(content)
        
    print("✅ Copied and patched Python scripts.")

def create_requirements():
    reqs = """
streamlit
openai
faiss-cpu
sentence-transformers
numpy
networkx
python-dotenv
    """.strip()
    with open(os.path.join(APP_DIR, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(reqs)
    print("✅ Created requirements.txt")

def create_dockerfile():
    dockerfile = """
# Base Python Image (Slim = Smaller)
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Calculated Cache Optimization)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Create a non-root user (Hugging Face Requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \\
    PATH=/home/user/.local/bin:$PATH

# Expose the Streamlit port
EXPOSE 7860

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
    """.strip()
    
    with open(os.path.join(APP_DIR, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile)
    print("✅ Created Dockerfile.")

if __name__ == "__main__":
    setup_directories()
    copy_data_files()
    process_python_files()
    create_requirements()
    create_dockerfile()
    print("\n🚀 Deployment package ready at: Day_12_Deployment/deployment_package/app")
