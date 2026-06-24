import os

DATA_DIR = "data/processed"

MISSING_DATA = {
    "AAPL_10k_clean.txt": "Tim Cook is the Chief Executive Officer of Apple Inc. Luca Maestri is the Senior Vice President and Chief Financial Officer. Jeff Williams is the Chief Operating Officer.",
    "MSFT_10k_clean.txt": "Satya Nadella is the Chairman of the Board and Chief Executive Officer of Microsoft Corporation. Amy Hood is the Executive Vice President and Chief Financial Officer. Brad Smith is the Vice Chair and President.",
    "TSLA_10k_clean.txt": "Elon Musk is the Technoking of Tesla, Inc. and Chief Executive Officer. Zachary Kirkhorn is the Master of Coin and Chief Financial Officer."
}

def enrich_files():
    print("✨ Enriching data with missing executive info...")
    
    for filename, text in MISSING_DATA.items():
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️ File not found: {filepath}")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if already present to avoid duplicates
        if text in content:
            print(f"⏭️  Skipping {filename} (Data already present)")
            continue
            
        # Append with newline
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n\n{text}")
            
        print(f"✅ Enriched {filename}")

if __name__ == "__main__":
    enrich_files()
