"""Tools for the agent nodes."""
from tavily import TavilyClient


def web_search(topic: str) -> str:
    """Search the web for visual references and hooks for a topic."""
    client = TavilyClient()
    response = client.search(
        query=f"{topic} visual design inspiration hooks",
        max_results=5,
        include_answer=True
    )
    
    # Build a summary from search results
    summary = f"Topic: {topic}\n\n"
    summary += f"Answer: {response.get('answer', 'No direct answer found')}\n\n"
    summary += "Visual references and hooks:\n"
    
    for result in response.get("results", []):
        summary += f"- {result.get('title', 'Untitled')}: {result.get('content', '')[:200]}\n"
    
    return summary
