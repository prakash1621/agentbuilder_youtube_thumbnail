"""Build the LangGraph state machine."""

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .state import ThumbnailState

from .nodes import (
    prompt_writer_node,
    generator_node,
    critic_node
)


def build_graph():
    """Build and compile the thumbnail designer graph."""

    graph = StateGraph(ThumbnailState)

    # Add nodes
    graph.add_node(
        "prompt_writer",
        prompt_writer_node
    )

    graph.add_node(
        "generator",
        generator_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    # Add edges
    graph.add_edge(
        START,
        "prompt_writer"
    )

    graph.add_edge(
        "prompt_writer",
        "generator"
    )

    graph.add_edge(
        "generator",
        "critic"
    )

    graph.add_edge(
        "critic",
        END
    )

    return graph.compile()