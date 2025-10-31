# visualize.py
import json
import networkx as nx
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def draw_repo_graph(index_file="indexed_repo.json", output_image="repo_graph.png"):
    """
    Loads the repo index and draws a graph of its structure.
    """
    try:
        with open(index_file, 'r') as f:
            repo_index = json.load(f)
    except FileNotFoundError:
        logging.error(f"'{index_file}' not found. Did you run 'indexer.py' first?")
        return
    except json.JSONDecodeError:
        logging.error(f"'{index_file}' is empty or corrupted. Please run 'indexer.py' again.")
        return

    G = nx.DiGraph() # Directed graph

    logging.info("Building graph from index...")
    for file_path, contents in repo_index.items():
        # Add the file as a root node for this part of the graph
        G.add_node(file_path, type='file')

        # Add class nodes and link them to the file
        for cls in contents.get('classes', []):
            class_name = cls['name']
            G.add_node(class_name, type='class')
            G.add_edge(file_path, class_name) # File -> Class

        # Add function nodes and link them to the file
        for func in contents.get('functions', []):
            func_name = func['name']
            G.add_node(func_name, type='function')
            G.add_edge(file_path, func_name) # File -> Function
            
        # Add method nodes and link them to their class
        for meth in contents.get('methods', []):
            meth_name = meth['name']
            class_name = meth.get('class_name')
            
            if class_name and G.has_node(class_name):
                G.add_node(meth_name, type='method')
                G.add_edge(class_name, meth_name) # Class -> Method
            elif class_name:
                logging.warning(f"Method '{meth_name}' references unknown class '{class_name}'")

    if G.number_of_nodes() == 0:
        logging.warning("Graph is empty. No nodes were found in the index.")
        return

    # --- Draw the graph ---
    logging.info(f"Drawing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges...")
    plt.figure(figsize=(16, 12))
    
    # Position nodes using a spring layout
    pos = nx.spring_layout(G, k=0.8, iterations=50) 
    
    # Color nodes by type
    colors = []
    for node in G.nodes():
        node_type = G.nodes[node]['type']
        if node_type == 'file':
            colors.append('#ffb3ba') # red
        elif node_type == 'class':
            colors.append('#baffc9') # green
        elif node_type == 'function':
            colors.append('#bae1ff') # blue
        elif node_type == 'method':
            colors.append('#ffffba') # yellow
        else:
            colors.append('#e0e0e0') # grey
    
    nx.draw_networkx(
        G,
        pos,
        with_labels=True,
        node_color=colors,
        node_size=3000,
        font_size=10,
        arrows=True,
        arrowstyle='->',
        arrowsize=15
    )
    plt.title("Repository Code Structure")
    plt.axis('off') # Hide the axes
    
    # Save the graph to a file
    plt.savefig(output_image)
    logging.info(f"✅ Graph saved to {output_image}")
    # You can also use plt.show() in a notebook
    # plt.show()
    

if __name__ == "__main__":
    draw_repo_graph()