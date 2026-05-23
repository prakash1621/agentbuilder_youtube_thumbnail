"""State schema for the thumbnail designer agent."""
import operator
from typing import Annotated, TypedDict


class IterationRecord(TypedDict):
    """Record of a single iteration."""
    iteration: int
    prompt: str
    image_path: str
    rating: int
    critique: str


class ThumbnailState(TypedDict):
    """State for the thumbnail designer graph."""
    topic: str
    prompt: str
    image_path: str
    rating: int
    critique: str
