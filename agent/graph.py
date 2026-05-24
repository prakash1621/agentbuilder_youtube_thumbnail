"""Build the LangGraph state machine."""
from langgraph.graph import StateGraph, START, END

from .state import ThumbnailState
from .nodes import (
    web_search_node,
    prompt_writer_node,
    generator_node,
    critic_node,
    saver_node,
    should_continue
)


def build_graph():
    """Build and compile the thumbnail designer graph."""
    graph = StateGraph(ThumbnailState)
    
    # Add nodes
    graph.add_node("web_search", web_search_node)
    graph.add_node("prompt_writer", prompt_writer_node)
    graph.add_node("generator", generator_node)
    graph.add_node("critic", critic_node)
    graph.add_node("saver", saver_node)
    
    # Add edges
    graph.add_edge(START, "web_search")
    graph.add_edge("web_search", "prompt_writer")
    graph.add_edge("prompt_writer", "generator")
    graph.add_edge("generator", "critic")
    
    # Conditional edge: loop or save
    graph.add_conditional_edges(
        "critic",
        should_continue,
        {
            "prompt_writer": "prompt_writer",
            "saver": "saver"
        }
    )
    
    graph.add_edge("saver", END)
    
    return graph.compile()
