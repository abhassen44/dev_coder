# visualize_dynamic.py
import json
import logging
import sys
from pyvis.network import Network

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def draw_dynamic_graph(index_file="indexed_repo.json", output_html="repo_graph_dynamic.html"):
    """
    Loads the repo index and draws a dynamic, interactive graph
    using pyvis.
    """
    try:
        with open(index_file, 'r') as f:
            repo_index = json.load(f)
    except FileNotFoundError:
        logging.error(f"'{index_file}' not found. Did you run 'indexer.py' first?")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"'{index_file}' is empty. Run 'indexer.py' again.")
        sys.exit(1)

    # Initialize pyvis network.
    # We're setting a dark background to match your screenshot's feel.
    net = Network(
        height="80vh", 
        width="100%", 
        heading="Dynamic Repository Structure", 
        directed=True,
        bgcolor="#222222",  # Dark background
        font_color="white"   # Light text
    )

    logging.info("Building dynamic graph from index...")
    if not repo_index:
        logging.warning("Index file is empty. No graph to generate.")
        return

    # --- Define node styles ---
    # Shapes: 'dot', 'square', 'database', 'box', 'text', 'diamond'
    styles = {
        'file': {'color': '#ff6e6e', 'shape': 'database', 'size': 20},
        'class': {'color': '#6effa8', 'shape': 'box', 'size': 15},
        'function': {'color': '#6e9bff', 'shape': 'dot', 'size': 10},
        'method': {'color': '#fffc6e', 'shape': 'dot', 'size': 10}
    }

    node_ids = set() # To track added nodes

    for file_path, contents in repo_index.items():
        # Add File Node
        if file_path not in node_ids:
            net.add_node(file_path, label=file_path, title=f"File: {file_path}", **styles['file'])
            node_ids.add(file_path)

        # Add Class Nodes and link to file
        for cls in contents.get('classes', []):
            class_name = cls['name']
            if class_name not in node_ids:
                net.add_node(class_name, label=class_name, title=f"Class: {class_name}", **styles['class'])
                node_ids.add(class_name)
            net.add_edge(file_path, class_name)

        # Add Function Nodes and link to file
        for func in contents.get('functions', []):
            func_name = func['name']
            # Create a unique ID for functions, as two files might have a 'main'
            node_id = f"{file_path}::{func_name}" 
            if node_id not in node_ids:
                net.add_node(node_id, label=func_name, title=f"Function: {func_name}", **styles['function'])
                node_ids.add(node_id)
            net.add_edge(file_path, node_id)
        
        # Add Method Nodes and link to their class
        for meth in contents.get('methods', []):
            meth_name = meth['name']
            class_name = meth.get('class_name')
            # Create a unique ID for methods
            node_id = f"{class_name}::{meth_name}"
            
            if class_name and class_name in node_ids:
                if node_id not in node_ids:
                    net.add_node(node_id, label=meth_name, title=f"Method: {meth_name}", **styles['method'])
                    node_ids.add(node_id)
                net.add_edge(class_name, node_id)
            elif class_name:
                logging.warning(f"Method '{meth_name}' references unknown class '{class_name}'")

    if not node_ids:
        logging.warning("Graph is empty. No nodes were found in the index.")
        return

    # Add physics-based layout options
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -40000,
          "centralGravity": 0.1,
          "springLength": 150
        },
        "solver": "barnesHut"
      },
      "interaction": {
        "navigationButtons": true,
        "tooltipDelay": 200
      }
    }
    """)

    # Save the graph to an HTML file
    net.save_graph(output_html)
    logging.info(f"✅ Dynamic graph saved! Open '{output_html}' in your browser.")

if __name__ == "__main__":
    # Make sure 'indexed_repo.json' exists by running 'indexer.py' first
    draw_dynamic_graph()