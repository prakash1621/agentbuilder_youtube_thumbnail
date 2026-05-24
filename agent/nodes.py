"""Node functions for the thumbnail designer graph."""
import base64
import os
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from .state import ThumbnailState, IterationRecord
from .prompts import PROMPT_WRITER_SYSTEM, CRITIC_SYSTEM
from .tools import web_search


class CriticOutput(BaseModel):
    """Structured output from the critic."""
    rating: int = Field(..., ge=1, le=10, description="Rating from 1 to 10")
    critique: str = Field(..., description="Detailed feedback on what to improve")


def web_search_node(state: ThumbnailState) -> dict:
    """Search the web for visual references and hooks."""
    print(f"\n Web Search: {state['topic']}")
    search_summary = web_search(state["topic"])
    return {"search_summary": search_summary}


def prompt_writer_node(state: ThumbnailState) -> dict:
    """Write or rewrite the DALL-E prompt."""
    print(f"\n Prompt Writer (Iteration {state['iteration']})")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Build context for the prompt writer
    context = f"Topic: {state['topic']}\n\nVisual References:\n{state['search_summary']}"
    
    # If this is a refinement iteration, include the previous critique
    if state["iteration"] > 1 and state["critique"]:
        context += f"\n\nPrevious Critique (fix these issues):\n{state['critique']}"
    
    messages = [
        HumanMessage(content=f"{PROMPT_WRITER_SYSTEM}\n\n{context}")
    ]
    
    response = llm.invoke(messages)
    prompt = response.content.strip()
    
    print(f"Generated prompt: {prompt[:100]}...")
    return {"prompt": prompt}


def generator_node(state: ThumbnailState) -> dict:
    """Generate the thumbnail image using GPT Image models."""
    print(f"\n Generator: Creating image (Iteration {state['iteration']})")
    
    from openai import OpenAI
    
    client = OpenAI()
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = state["topic"].lower().replace(" ", "_")[:30]
    output_dir = Path(f"outputs/{timestamp}_{topic_slug}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Try different image models with appropriate sizes
    models_config = [
        {"model": "gpt-image-2", "size": "1792x1024"},
        {"model": "gpt-image-1.5", "size": "1024x1024"},
        {"model": "gpt-image-1", "size": "1024x1024"},
    ]
    
    response = None
    used_model = None
    
    for config in models_config:
        try:
            model = config["model"]
            size = config["size"]
            print(f"Trying model: {model} with size {size}")
            response = client.images.generate(
                model=model,
                prompt=state["prompt"],
                size=size,
                n=1
            )
            used_model = model
            print(f"✓ Successfully generated with {model}")
            break
        except Exception as e:
            print(f"✗ {model} failed: {str(e)[:100]}")
            continue
    
    if response is None:
        raise RuntimeError("All image generation models failed")
    
    # Handle different response formats (URL or base64)
    image_data = response.data[0]
    image_path = output_dir / f"iter_{state['iteration']}.png"
    
    if hasattr(image_data, 'url') and image_data.url:
        # Response contains URL - download it
        import requests
        print(f"Downloading image from URL...")
        img_response = requests.get(image_data.url)
        image_path.write_bytes(img_response.content)
    elif hasattr(image_data, 'b64_json') and image_data.b64_json:
        # Response contains base64 encoded image
        import base64
        print(f"Decoding base64 image...")
        image_bytes = base64.b64decode(image_data.b64_json)
        image_path.write_bytes(image_bytes)
    else:
        raise RuntimeError(f"No image URL or base64 data returned from {used_model}")
    
    print(f"Image saved to: {image_path}")
    
    return {
        "image_path": str(image_path),
        "iteration": state["iteration"] + 1
    }


def critic_node(state: ThumbnailState) -> dict:
    """Evaluate the generated thumbnail."""
    print(f"\n Critic: Evaluating image")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    
    # Convert image to base64
    img_b64 = base64.b64encode(Path(state["image_path"]).read_bytes()).decode()
    
    # Create structured output model
    structured_llm = llm.with_structured_output(CriticOutput)
    
    messages = [
        HumanMessage(content=[
            {"type": "text", "text": CRITIC_SYSTEM},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
        ])
    ]
    
    response = structured_llm.invoke(messages)
    
    print(f"Rating: {response.rating}/10")
    print(f"Critique: {response.critique[:100]}...")
    
    return {
        "rating": response.rating,
        "critique": response.critique
    }


def should_continue(state: ThumbnailState) -> str:
    """Decide whether to continue iterating or save."""
    rating = state["rating"]
    iteration = state["iteration"]
    target = state["target_rating"]
    max_iter = state["max_iterations"]
    
    print(f"\n Decision: rating={rating}, iteration={iteration}, target={target}, max={max_iter}")
    
    if rating >= target or iteration >= max_iter:
        print("→ Proceeding to saver")
        return "saver"
    else:
        print("→ Looping back to prompt_writer")
        return "prompt_writer"


def saver_node(state: ThumbnailState) -> dict:
    """Save the best thumbnail and generate report."""
    print(f"\nSaver: Finalizing outputs")
    
    # Append current iteration to history
    current_record = IterationRecord(
        iteration=state["iteration"] - 1,
        prompt=state["prompt"],
        image_path=state["image_path"],
        rating=state["rating"],
        critique=state["critique"]
    )
    
    history = state.get("history", []) + [current_record]
    
    # Find best image
    best_record = max(history, key=lambda x: x["rating"])
    best_image_path = best_record["image_path"]
    
    # Get output directory from best image path
    output_dir = Path(best_image_path).parent
    
    # Copy best image as final.png
    final_path = output_dir / "final.png"
    final_path.write_bytes(Path(best_image_path).read_bytes())
    print(f"Final image saved to: {final_path}")
    
    # Generate report
    report_path = output_dir / "report.md"
    report_content = f"""# YouTube Thumbnail Designer Report

## Topic
{state['topic']}

## Summary
- Total iterations: {len(history)}
- Best rating: {best_record['rating']}/10
- Target rating: {state['target_rating']}/10

## Iteration History

"""
    
    for record in history:
        report_content += f"""### Iteration {record['iteration']}
- **Rating**: {record['rating']}/10
- **Image**: `{Path(record['image_path']).name}`
- **Prompt**: {record['prompt'][:200]}...
- **Critique**: {record['critique']}

"""
    
    report_content += f"""## Final Selection
Best thumbnail: `{Path(best_image_path).name}` (Rating: {best_record['rating']}/10)
"""
    
    report_path.write_text(report_content)
    print(f"Report saved to: {report_path}")
    
    return {
        "history": history,
        "best_image_path": str(final_path),
        "best_rating": best_record["rating"]
    }
