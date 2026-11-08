"""Policy helpers for chatbot multimodal preprocessing."""

from .caption_quality import (
    CaptionAssessment,
    CaptionQualityConfig,
    assess_caption,
    count_meaningful,
    count_placeholders,
    is_usable,
)
from .fallback import can_borrow_other_media, can_use_thumbnail
from .models import Decision, MediaItem, PolicyConfig
from .policy import choose_caption_mode, decide, should_retry_caption

__version__ = "0.2.0"

__all__ = [
    "CaptionAssessment",
    "CaptionQualityConfig",
    "Decision",
    "MediaItem",
    "PolicyConfig",
    "assess_caption",
    "can_borrow_other_media",
    "can_use_thumbnail",
    "choose_caption_mode",
    "count_meaningful",
    "count_placeholders",
    "decide",
    "is_usable",
    "should_retry_caption",
]
