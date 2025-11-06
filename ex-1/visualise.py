import os
import json
import logging
from pyvis.network import Network

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_html_from_index(index_file="indexed_repo.json", output_html="repo_mindmap.html"):
    """
    Generates a hierarchical, interactive HTML mindmap visualization
    from the indexed_repo.json file (assumed to be in the same directory).
    Nodes for functions, classes, and methods will show code snippets on hover.
    """

    # --- Load JSON ---
    if not os.path.exists(index_file):
        logging.error(f"❌ '{index_file}' not found. Make sure it exists in this folder.")
        return

    with open(index_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logging.error("❌ Invalid JSON format in indexed_repo.json.")
            return

    repo_name = data.get("repository", "Unknown Repository")
    files_data = data.get("files", [])
    commits = data.get("commitHistory", [])

    logging.info(f"📦 Loaded repository index for '{repo_name}'")

    # --- Initialize Visualization ---
    net = Network(
        height="90vh",
        width="100%",
        directed=True,
        bgcolor="#0e1117",
        font_color="#e8e8e8",
        heading=f"Repository Mindmap — {repo_name}"
    )

    # Physics OFF → more tree-like layout
    net.toggle_physics(False)

    # --- Node styles ---
    styles = {
        "repo": {"color": "#facc15", "shape": "box", "size": 30},
        "folder": {"color": "#10b981", "shape": "ellipse", "size": 20},
        "file": {"color": "#3b82f6", "shape": "dot", "size": 14},
        "class": {"color": "#ef4444", "shape": "diamond", "size": 12},
        "function": {"color": "#22d3ee", "shape": "dot", "size": 10},
        "method": {"color": "#a855f7", "shape": "dot", "size": 9},
        "commit": {"color": "#f97316", "shape": "triangle", "size": 10},
    }

    # Add root node (the repository itself)
    net.add_node("repo_root", label=repo_name, title=f"Repository: {repo_name}", **styles["repo"])

    # --- Detect if files is list or dict ---
    if isinstance(files_data, dict):
        iterable = files_data.items()
    elif isinstance(files_data, list):
        iterable = [(f["path"], f) for f in files_data]
    else:
        logging.error("❌ Invalid format for 'files' key.")
        return

    # --- Build hierarchical graph ---
    for filepath, filedata in iterable:
        parts = filepath.split("/")
        current_parent = "repo_root"

        for i, part in enumerate(parts):
            sub_path = "/".join(parts[:i + 1])
            node_id = f"path::{sub_path}"

            if i < len(parts) - 1:
                node_type = "folder"
                title = f"Folder: {part}"
            else:
                node_type = "file"
                title = f"File: {filepath}"

            if node_id not in net.node_map:
                net.add_node(node_id, label=part, title=title, **styles[node_type])
                net.add_edge(current_parent, node_id)

            current_parent = node_id

        # --- MODIFICATION: Add AST-level details with code snippets ---
        if isinstance(filedata, dict):
            
            # --- Handle Classes ---
            for cls in filedata.get("classes", []):
                cls_name = cls.get("name", "Unknown Class")
                cls_id = f"class::{filepath}::{cls_name}"
                
                # Get code snippet for the tooltip
                cls_code = cls.get("code_snippet", "No code snippet available.")
                cls_title = f"Class: {cls_name}\n\n{cls_code}"
                
                net.add_node(cls_id, label=cls_name, title=cls_title, **styles["class"])
                net.add_edge(current_parent, cls_id)

                # --- Handle Methods ---
                for method in cls.get("methods", []):
                    method_name = "Unknown Method"
                    method_title = ""
                    
                    # Handle new format (dict with details)
                    if isinstance(method, dict):
                        method_name = method.get("name", "Unknown Method")
                        method_code = method.get("code_snippet", "No code snippet available.")
                        method_title = f"Method: {method_name}\n\n{method_code}"
                    
                    # Handle old format (simple string)
                    elif isinstance(method, str):
                        method_name = method.strip()
                        method_title = f"Method in {cls_name}: {method_name}\n(No code snippet)"
                    
                    # Create a unique ID based on file, class, and method
                    method_id = f"method::{filepath}::{cls_name}::{method_name}"
                    net.add_node(method_id, label=method_name, title=method_title, **styles["method"])
                    net.add_edge(cls_id, method_id)

            # --- Handle Functions ---
            for fn in filedata.get("functions", []):
                fn_name = fn.get("name", "Unknown Function")
                fn_id = f"func::{filepath}::{fn_name}"
                
                # Get code snippet for the tooltip
                fn_code = fn.get("code_snippet", "No code snippet available.")
                fn_title = f"Function: {fn_name}\n\n{fn_code}"
                
                net.add_node(fn_id, label=fn_name, title=fn_title, **styles["function"])
                net.add_edge(current_parent, fn_id)

    # --- Optional: add commits ---
    if commits:
        prev_commit = None
        for commit in commits[:8]:  # Limit to first few for clarity
            cid = f"commit::{commit['sha'][:8]}"
            net.add_node(
                cid,
                label=commit['sha'][:7],
                title=f"{commit['message']}\nAuthor: {commit['author']}\nDate: {commit['date']}",
                **styles["commit"]
            )
            net.add_edge("repo_root", cid)
            if prev_commit:
                net.add_edge(prev_commit, cid)
            prev_commit = cid

    # --- Layout Settings ---
    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "LR",
          "sortMethod": "hubsize",
          "levelSeparation": 200,
          "nodeSpacing": 150
        }
      },
      "interaction": {
        "navigationButtons": true,
        "keyboard": true,
        "tooltipDelay": 200
      }
    }
    """)

    # --- Save and Report ---
    net.save_graph(output_html)
    logging.info(f"✅ Mindmap HTML generated: {output_html}")
    logging.info(f"Files visualized: {len(list(iterable))}")


if __name__ == "__main__":
    generate_html_from_index()