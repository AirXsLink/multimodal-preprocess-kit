"""Data models for multimodal preprocessing decisions."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class MediaItem:
    """One media item as it arrives in a chatbot pipeline.

    ``local_path`` is metadata only. This library never opens, decodes or
    uploads it; it exists so callers can implement their own fetching layer.
    """

    id: str
    kind: Literal["image", "sticker", "screenshot"]
    local_path: Optional[str] = None
    caption: Optional[str] = None
    caption_status: Literal["ready", "pending", "failed", "too_short"] = "pending"
    received_at: float = 0.0
    sender_key: Optional[str] = None


@dataclass
class PolicyConfig:
    """Tunable thresholds for the preprocessing policy.

    ``long_image_max_edge`` and ``long_image_max_tokens`` are reserved for
    callers that resize or budget images themselves; v0.1 does not enforce
    them because it never decodes an image.
    """

    min_caption_chars: int = 40
    max_defer_seconds: int = 90
    long_image_min_edge: int = 700
    long_image_max_edge: int = 1400
    long_image_max_tokens: int = 900
    allow_thumbnail_fallback: bool = True
    allow_borrow_other_media: bool = False


@dataclass
class Decision:
    """The outcome of evaluating one media item."""

    action: Literal["push_now", "defer", "push_without_media", "retry_caption", "drop_media"]
    reason: str
    retry_after: Optional[float] = None
    caption_mode: Optional[Literal["auto", "transcribe", "describe"]] = None
