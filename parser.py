# parser.py
# This script uses the 'tree-sitter-language-pack' library, which is the
# simplest and most modern way to use Tree-sitter in Python.
#
# This library comes with pre-compiled grammars, so you do NOT need a
# separate build or compile step (e.g., no 'compile_grammars.py').
#
# To use this, just install the necessary packages:
# pip install tree-sitter tree-sitter-language-pack

from tree_sitter_language_pack import get_parser, get_language

def analyze_python_code(code_snippet):
    """
    Analyzes a Python code snippet using a pre-compiled parser from
    the tree-sitter-language-pack.
    """
    print("\n--- Analyzing Code ---")
    print(f"Code Snippet:\n```python\n{code_snippet}\n```")

    try:
        # Get a ready-to-use parser for Python. This function handles
        # finding the pre-compiled grammar library automatically.
        python_parser = get_parser('python')

        # Parse the code snippet
        tree = python_parser.parse(bytes(code_snippet, "utf8"))
        root_node = tree.root_node

        print("\n--- Analysis Results ---")
        print(f"✓ Code parsed successfully!")
        print(f"  child_count: {root_node.child_count}")


    except Exception as e:
        print(f"\n✗ ERROR: Could not parse the code.")
        print(f"  Please make sure you have run 'pip install tree-sitter tree-sitter-language-pack'")
        print(f"  Details: {e}")


if __name__ == "__main__":
    # Define a sample piece of Python code to test with
    sample_code = """
def calculate_sum(a, b):
    # This is a simple function
    result = a + b
    return result

print(calculate_sum(5, 10))
"""
    analyze_python_code(sample_code)
