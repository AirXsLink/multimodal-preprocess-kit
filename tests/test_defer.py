"""Pending-message deferral tests."""

import pytest

from mm_preprocess_kit.models import MediaItem, PolicyConfig
from mm_preprocess_kit.policy import decide


def test_pending_within_window_defers() -> None:
    media = MediaItem(id="m1", kind="image", caption_status="pending", received_at=100.0)
    decision = decide(media, now=130.0, cfg=PolicyConfig())
    assert decision.action == "defer"
    assert decision.reason == "caption_pending"
    assert decision.retry_after == pytest.approx(60.0)


def test_pending_past_window_pushes_without_media() -> None:
    media = MediaItem(id="m2", kind="image", caption_status="pending", received_at=0.0)
    decision = decide(media, now=100.0, cfg=PolicyConfig())
    assert decision.action == "push_without_media"
    assert decision.reason == "caption_timeout"
