"""Build the LangGraph state machine."""

 
from asyncio import graph
import web_search_node,saver_node

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .state import ThumbnailState

from .nodes import (
    prompt_writer_node,
    generator_n,
    saver_node,
    saver_nodeode,
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
    "web_search"
)

    graph.add_edge(
        "web_search",
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
    "saver"
)

    graph.add_edge(
    "saver",
    END
)

    graph.add_node(
    "web_search",
    web_search_node
     )

    graph.add_node(
    "saver",
    saver_node
    )

    return graph.compile()