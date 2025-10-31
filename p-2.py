# parser.py
# Universal Python code analyzer using Tree-sitter.
# Requires:
#   pip install tree-sitter tree-sitter-language-pack

from tree_sitter_language_pack import get_parser, get_language
from tree_sitter import Query, QueryCursor


def analyze_python_code(code_snippet):
    print("\n=== Python Code Analysis ===")
    print(f"\nCode Snippet:\n```python\n{code_snippet.strip()}\n```")

    try:
        parser = get_parser('python')
        language = get_language('python')
        tree = parser.parse(bytes(code_snippet, "utf8"))
        root = tree.root_node

        print("\n--- Parsing Info ---")
        print("✓ Code parsed successfully!")
        print(f"Root type: {root.type}, total length: {root.end_byte} bytes")

        # --- Updated Queries (100% compatible) ---
        queries = {
            "Functions": """
                (function_definition
                    name: (identifier) @function.name)
            """,
            "Classes": """
                (class_definition
                    name: (identifier) @class.name)
            """,
            "Function Parameters": """
                (function_definition
                    parameters: (parameters
                        (identifier) @param.name))
            """,
            "Function Calls": """
                (call
                    function: (identifier) @call.name)
            """,
            # ✅ FIXED import query
            "Imports": """
                [
                    (import_statement (dotted_name) @import.module)
                    (import_statement (aliased_import (dotted_name) @import.alias))
                    (import_from_statement (dotted_name) @from.module)
                ]
            """,
            "Return Statements": """
                (return_statement
                    (expression) @return.expr)
            """,
            "Assignments": """
                (assignment
                    left: (identifier) @var.name)
            """,
                        "Decorators": """
                                [
                                    ;; simple decorator like @name
                                    (decorator (identifier) @decorator.name)
                                    ;; decorator that's a call: @name(...) or @module.name(...)
                                    (decorator (call (identifier) @decorator.name))
                                    (decorator (call (attribute (identifier) @decorator.name)))
                                    ;; decorator that's an attribute: @module.name
                                    (decorator (attribute (identifier) @decorator.name))
                                    ;; fallback: capture the whole decorator node text
                                    (decorator) @decorator.node
                                ]
                        """,
            "Loops": """
                [
                    (for_statement (identifier) @loop.var)
                    (while_statement) @while.loop
                ]
            """,
            "If Conditions": """
                (if_statement
                    condition: (_) @if.condition)
            """,
        }


        results = {}
        for name, query_str in queries.items():
            # Build Query and QueryCursor per-query so a single bad pattern
            # doesn't abort the whole analysis. Report which query fails.
            try:
                query = Query(language, query_str)
            except Exception as e:
                print(f"\n✗ QUERY ERROR for '{name}': {e}")
                results[name] = []
                continue

            try:
                cursor = QueryCursor(query)
                matches = cursor.matches(root)
            except Exception as e:
                print(f"\n✗ QueryCursor error for '{name}': {e}")
                results[name] = []
                continue

            captured = []
            for pattern_index, captures in matches:
                for capture_name, nodes in captures.items():
                    for node in nodes:
                        try:
                            if node.text:
                                text = node.text.decode("utf8").strip()
                                captured.append(text)
                        except Exception:
                            # defensive: skip nodes we can't decode
                            continue

            results[name] = list(sorted(set(captured)))

        # --- Output ---
        print("\n--- Analysis Results ---")
        for key, items in results.items():
            print(f"\n{key}:")
            if items:
                for item in items:
                    print(f"  • {item}")
            else:
                print("  (none found)")

    except Exception as e:
        print(f"\n✗ ERROR: Could not parse the code.")
        print(f"  Make sure you installed 'tree-sitter' and 'tree-sitter-language-pack'")
        print(f"  Details: {e}")


if __name__ == "__main__":
    sample_code = """
import os
from math import sqrt

@staticmethod
def calculate_sum(a, b):
    result = a + b
    return result

class Calculator:
    def multiply(self, x, y):
        return x * y

def square_root(x):
    return sqrt(x)

for i in range(5):
    print(calculate_sum(i, 2))
"""
    analyze_python_code(sample_code)
