"""Node functions for the thumbnail designer graph."""

import base64
from pathlib import Path
from datetime import datetime
from .tools import web_search

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from .state import ThumbnailState
from .prompts import PROMPT_WRITER_SYSTEM, CRITIC_SYSTEM


class CriticOutput(BaseModel):
    """Structured output from the critic."""
    
    rating: int = Field(
        ...,
        ge=1,
        le=10,
        description="Rating from 1 to 10"
    )

    critique: str = Field(
        ...,
        description="Detailed feedback on what to improve"
    )


def prompt_writer_node(state: ThumbnailState) -> dict:
    """Generate thumbnail prompt."""

    print("\n✍️ Prompt Writer")

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7
    )

    context = f"""
    Topic: {state['topic']}

    Visual Inspiration:
        {state['search_summary']}
    """

    messages = [
        HumanMessage(
            content=f"{PROMPT_WRITER_SYSTEM}\n\n{context}"
        )
    ]

    response = llm.invoke(messages)

    prompt = response.content.strip()

    print(f"Generated prompt: {prompt[:100]}...")

    return {
        "prompt": prompt
    }

def saver_node(state: ThumbnailState) -> dict:
    """Save final thumbnail."""

    print("\n💾 Saver")

    final_path = Path(state["image_path"]).parent / "final.png"

    final_path.write_bytes(
        Path(state["image_path"]).read_bytes()
    )

    print(f"Final image saved to: {final_path}")

    return {
        "best_image_path": str(final_path)
    }


def web_search_node(state: ThumbnailState) -> dict:
    """Search web for thumbnail inspiration."""

    print("\n🔍 Web Search")

    search_summary = web_search(
        state["topic"]
    )

    return {
        "search_summary": search_summary
    }

def generator_node(state: ThumbnailState) -> dict:
    """Generate thumbnail image."""

    print("\n🎨 Generator")

    from openai import OpenAI

    client = OpenAI()

    # Create output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    topic_slug = state["topic"].lower().replace(" ", "_")[:30]

    output_dir = Path(f"outputs/{timestamp}_{topic_slug}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate image
    response = client.images.generate(
        model="gpt-image-1",
        prompt=state["prompt"],
        size="1536x1024",
        n=1
    )

    image_data = response.data[0]

    image_path = output_dir / "thumbnail.png"

    # URL response
    if hasattr(image_data, "url") and image_data.url:

        import requests

        img_response = requests.get(image_data.url)

        image_path.write_bytes(img_response.content)

    # Base64 response
    elif hasattr(image_data, "b64_json") and image_data.b64_json:

        image_bytes = base64.b64decode(image_data.b64_json)

        image_path.write_bytes(image_bytes)

    else:
        raise RuntimeError("No image returned")

    print(f"Image saved to: {image_path}")

    return {
        "image_path": str(image_path)
    }


def critic_node(state: ThumbnailState) -> dict:
    """Evaluate generated thumbnail."""

    print("\n👁️ Critic")

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3
    )

    # Convert image to base64
    img_b64 = base64.b64encode(
        Path(state["image_path"]).read_bytes()
    ).decode()

    structured_llm = llm.with_structured_output(
        CriticOutput
    )

    messages = [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": CRITIC_SYSTEM
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}"
                    }
                }
            ]
        )
    ]

    response = structured_llm.invoke(messages)

    print(f"Rating: {response.rating}/10")

    print(f"Critique: {response.critique}")

    return {
        "rating": response.rating,
        "critique": response.critique
    }