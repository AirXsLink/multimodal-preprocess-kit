"""Decision policies for caption readiness and pending-message deferral.

Every function here is pure: no network, no filesystem, no wall clock. Callers
pass ``now`` in, which keeps decisions reproducible and easy to test.
"""

from typing import Literal, Optional

from .models import Decision, MediaItem, PolicyConfig


def should_retry_caption(caption: Optional[str], cfg: PolicyConfig) -> bool:
    """Return True when a caption is missing or shorter than the threshold."""
    if caption is None:
        return True
    return len(caption.strip()) < cfg.min_caption_chars


def choose_caption_mode(
    width: int, height: int, cfg: PolicyConfig
) -> Literal["auto", "transcribe", "describe"]:
    """Pick a caption mode for a screenshot of the given pixel size.

    Long images are transcribed line by line; everything else is described.
    ``"auto"`` is never returned here; it is a pass-through value only.
    """
    if max(width, height) >= cfg.long_image_min_edge:
        return "transcribe"
    return "describe"


def decide(media: MediaItem, now: float, cfg: PolicyConfig) -> Decision:
    """Decide what to do with one media item at time ``now``.

    ``now`` and ``media.received_at`` are floats in the same unit (seconds).

    Resolution order, gated by caption status so that a short or missing
    caption cannot shadow the deferral or failure branches:

    1. ``failed``            -> ``drop_media``
    2. ``too_short``         -> ``retry_caption``
    3. ``ready`` + short     -> ``retry_caption``
    4. ``pending``, in time  -> ``defer``
    5. ``pending``, too late -> ``push_without_media``
    6. ``ready``, non-empty  -> ``push_now``
    7. anything else         -> ``push_without_media`` (``unknown_state``)

    A screenshot gets ``caption_mode="auto"`` because this module never learns
    an item's pixel size; the caller resolves ``"auto"`` with
    :func:`choose_caption_mode` once the real width and height are known.
    """
    status = media.caption_status

    if status == "failed":
        return Decision(action="drop_media", reason="caption_failed")

    if status == "too_short":
        return Decision(action="retry_caption", reason="caption_too_short")

    if status == "ready" and should_retry_caption(media.caption, cfg):
        return Decision(action="retry_caption", reason="caption_too_short")

    if status == "pending":
        waited = now - media.received_at
        if waited <= cfg.max_defer_seconds:
            return Decision(
                action="defer",
                reason="caption_pending",
                retry_after=cfg.max_defer_seconds - waited,
            )
        return Decision(action="push_without_media", reason="caption_timeout")

    if status == "ready" and media.caption:
        caption_mode: Optional[Literal["auto", "transcribe", "describe"]] = (
            "auto" if media.kind == "screenshot" else None
        )
        return Decision(action="push_now", reason="caption_ready", caption_mode=caption_mode)

    return Decision(action="push_without_media", reason="unknown_state")
