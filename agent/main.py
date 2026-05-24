"""Entry point for the thumbnail designer agent."""

import argparse

from .graph import build_graph
from .state import ThumbnailState


def main():
    """Run the thumbnail designer agent."""

    parser = argparse.ArgumentParser(
        description="YouTube Thumbnail Designer"
    )

    parser.add_argument(
        "topic",
        help="Video topic for thumbnail design"
    )

    args = parser.parse_args()

    # Build graph
    graph = build_graph()

    # Initial state
    initial_state: ThumbnailState = {
    "topic": args.topic,
    "search_summary": "",
    "prompt": "",
    "image_path": "",
    "rating": 0,
    "critique": "",
    "iteration": 1,
    "target_rating": 8,
    "max_iterations": 3,
    "best_image_path": ""
}

    print("\n🎬 Starting YouTube Thumbnail Designer")
    print(f"Topic: {args.topic}")

    # Run graph
    result = graph.invoke(initial_state)

    print("\n✅ Complete!")

    print(f"Image Path: {result['image_path']}")

    print(f"Rating: {result['rating']}/10")

    print(f"Critique: {result['critique']}")


if __name__ == "__main__":
    main()