# indexer.py
import os
import json
import logging
from pathlib import Path

# Import the main classes from your p-3.py file
from p-3 import Treesitter, LanguageEnum

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def serialize_nodes(nodes):
    """
    Converts a list of TreesitterClassNode or TreesitterMethodNode
    objects into a simple list of dictionaries for JSON.
    """
    output = []
    for node in nodes:
        # We only serialize the data we need, not the internal 'node' object
        if hasattr(node, 'method_declarations'): # It's a ClassNode
            output.append({
                "name": node.name,
                "type": "class",
                "methods": [decl.split('\n', 1)[0] for decl in node.method_declarations] # Just get method signature
            })
        elif hasattr(node, 'method_source_code'): # It's a MethodNode
             output.append({
                "name": node.name,
                "type": "function" if node.class_name is None else "method",
                "class_name": node.class_name,
                "doc_comment": node.doc_comment
            })
    return output

def index_repository(repo_path, output_file="indexed_repo.json"):
    """
    Scans a directory for Python files, parses them, and saves
    the structure to a JSON file.
    """
    
    # Initialize the Python parser from p-3.py
    try:
        ts_parser = Treesitter(LanguageEnum.PYTHON)
    except Exception as e:
        logging.error(f"Failed to initialize parser. Did you run 'pip install -r requirements.txt' from p-3.py? Error: {e}")
        return

    repo_index = {}
    
    # Use pathlib.Path.rglob to recursively find all .py files
    logging.info(f"Starting to index repository at: {repo_path}")
    root_path = Path(repo_path)
    
    for file_path in root_path.rglob("*.py"):
        # Get a relative path to use as the key in our JSON
        relative_path = str(file_path.relative_to(root_path))
        logging.info(f"Parsing: {relative_path}")

        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            # Use the parse method from p-3.py
            classes, methods = ts_parser.parse(file_bytes)
            
            # Store the results in our index
            repo_index[relative_path] = {
                "classes": serialize_nodes(classes),
                "functions": serialize_nodes([m for m in methods if m.class_name is None]), # Standalone functions
                "methods": serialize_nodes([m for m in methods if m.class_name is not None]) # Class methods
            }

        except Exception as e:
            logging.error(f"Failed to parse {relative_path}: {e}")

    # Write the final index to the JSON file
    with open(output_file, 'w', encoding='utf8') as f:
        json.dump(repo_index, f, indent=2)
        
    logging.info(f"✅ Indexing complete! Data saved to {output_file}")

if __name__ == "__main__":
    # --- IMPORTANT ---
    # Create a folder named 'my_test_project' and put some
    # .py files in it to test this.
    #
    # Example:
    # my_test_project/
    # |-- utils.py
    # |-- main.py
    #
    PROJECT_DIR = "my_test_project" # <--- Point this to your code repo
    
    if not os.path.exists(PROJECT_DIR):
        logging.warning(f"Test directory '{PROJECT_DIR}' not found.")
        logging.warning("Please create it and add some Python files to scan.")
    else:
        index_repository(PROJECT_DIR)