"""Generate a diagram of the graph."""
from pathlib import Path
from .graph import build_graph


def main():
    """Generate and save the graph diagram."""
    graph = build_graph()
    
    # Generate PNG
    png_data = graph.get_graph().draw_mermaid_png()
    
    # Save to repo root
    output_path = Path("graph.png")
    output_path.write_bytes(png_data)
    
    print(f" Graph diagram saved to: {output_path}")


if __name__ == "__main__":
    main()
