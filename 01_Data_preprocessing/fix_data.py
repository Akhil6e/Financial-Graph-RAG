import os
import re

DATA_DIR = "data/processed"

def clean_file(filepath):
    # Read with error ignoring to drop binary garbage
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    cleaned_lines = []
    
    # Header skip flag
    header_done = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Scorched Earth Filtering
        
        # 1. Kill XML/Code/URLs instantly
        if any(x in line for x in ["xmlns", "http", "width=", "style=", "background", "margin", "<", ">", "{", "}"]):
            continue
            
        # 2. Kill System Headers (even if they look like text)
        if any(x in line.upper() for x in ["ACCESSION NUMBER", "CONFORMED", "SEC FILE", "FILM NUMBER", "INDEX KEY"]):
            continue

        # 3. Kill Table Rows (numbers, dates, currency)
        if re.search(r'\d{2,}', line) and len(line) < 100: # Short lines with numbers are usually table data
            continue
            
        # 4. Symbol Ratio (Code usually has many symbols)
        if len(line) > 0:
            symbols = len(re.findall(r'[^a-zA-Z0-9\s\.,]', line))
            if symbols / len(line) > 0.05: # Very strict: >5% symbols = garbage
                continue

        # 5. Sentence Structure Check
        # Must start with Capital
        if not line[0].isupper():
            continue
            
        # Must end with sentence punctuation
        if not line.endswith(('.', '"', ':', ';')):
            continue
            
        # Must be long enough to be a sentence
        if len(line.split()) < 5:
            continue
            
        # REPLACEMENT: Kill known bad artifacts
        line = line.replace('\ufffd', '') # Remove replacement chars (diamonds)
        
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)

def run_cleaning():
    if not os.path.exists(DATA_DIR):
        print(f"❌ Directory not found: {DATA_DIR}")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith("_clean.txt")]
    print(f"🧹 Cleaning {len(files)} files in {DATA_DIR}...")
    
    for filename in files:
        path = os.path.join(DATA_DIR, filename)
        try:
            # First, strip any binary garbage from previous runs
            clean_text = clean_file(path)
            
            # Key Fix: Enforce UTF-8 to kill Windows encoding bugs
            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_text)
                
            print(f"✅ Cleaned {filename}: {len(clean_text)} chars remaining")
            
        except Exception as e:
            print(f"❌ Error cleaning {filename}: {e}")

if __name__ == "__main__":
    run_cleaning()
