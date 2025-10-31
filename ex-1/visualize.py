# Wrapper to support American spelling and both visualise.py APIs
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_draw = None
try:
    from visualise import draw_repo_graph as _draw
except Exception:
    try:
        from visualise import draw_dynamic_graph as _draw
    except Exception as e:
        logging.error(f"Failed to import a draw function from visualise.py: {e}")
        raise

if __name__ == "__main__":
    _draw()
