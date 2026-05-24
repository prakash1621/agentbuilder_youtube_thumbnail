"""Entry point for the thumbnail designer agent."""
import argparse
from .graph import build_graph
from .state import ThumbnailState


def main():
    """Run the thumbnail designer agent."""
    parser = argparse.ArgumentParser(description="YouTube Thumbnail Designer")
    parser.add_argument("topic", help="Video topic for thumbnail design")
    parser.add_argument("--stream", action="store_true", help="Stream output")
    parser.add_argument("--target-rating", type=int, default=8, help="Target rating (1-10)")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum iterations")
    
    args = parser.parse_args()
    
    # Build graph
    graph = build_graph()
    
    # Initialize state
    initial_state: ThumbnailState = {
        "topic": args.topic,
        "search_summary": "",
        "prompt": "",
        "image_path": "",
        "rating": 0,
        "critique": "",
        "iteration": 1,
        "target_rating": args.target_rating,
        "max_iterations": args.max_iterations,
        "history": [],
        "best_rating": 0,
        "best_image_path": ""
    }
    
    # Run graph
    if args.stream:
        print(f"\n Starting YouTube Thumbnail Designer")
        print(f"Topic: {args.topic}")
        print(f"Target rating: {args.target_rating}/10")
        print(f"Max iterations: {args.max_iterations}\n")
        
        for output in graph.stream(initial_state):
            for key, value in output.items():
                print(f"\n[{key}]")
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k not in ["history"]:
                            print(f"  {k}: {v}")
    else:
        print(f"\n Starting YouTube Thumbnail Designer")
        print(f"Topic: {args.topic}")
        print(f"Target rating: {args.target_rating}/10")
        print(f"Max iterations: {args.max_iterations}\n")
        
        result = graph.invoke(initial_state)
        
        print(f"\n Complete!")
        print(f"Best rating: {result['best_rating']}/10")
        print(f"Final image: {result['best_image_path']}")


if __name__ == "__main__":
    main()
