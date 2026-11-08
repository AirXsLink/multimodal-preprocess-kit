"""Decision actions: every branch of ``decide`` gets an assertion."""

from mm_preprocess_kit.models import MediaItem, PolicyConfig
from mm_preprocess_kit.policy import decide


def test_failed_drops_media() -> None:
    media = MediaItem(id="m", kind="image", caption_status="failed")
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "drop_media"
    assert decision.reason == "caption_failed"


def test_too_short_retries() -> None:
    media = MediaItem(id="m", kind="image", caption_status="too_short")
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "retry_caption"
    assert decision.reason == "caption_too_short"


def test_ready_short_caption_retries() -> None:
    media = MediaItem(id="m", kind="image", caption_status="ready", caption="x" * 10)
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "retry_caption"
    assert decision.reason == "caption_too_short"


def test_ready_caption_pushes_now() -> None:
    media = MediaItem(id="m", kind="image", caption_status="ready", caption="x" * 60)
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "push_now"
    assert decision.reason == "caption_ready"
    assert decision.caption_mode is None


def test_screenshot_carries_auto_mode() -> None:
    media = MediaItem(
        id="m", kind="screenshot", caption_status="ready", caption="x" * 60
    )
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "push_now"
    assert decision.caption_mode == "auto"


def test_unknown_state_pushes_without_media() -> None:
    media = MediaItem(id="m", kind="image", caption_status="bogus")  # type: ignore[arg-type]
    decision = decide(media, now=0.0, cfg=PolicyConfig())
    assert decision.action == "push_without_media"
    assert decision.reason == "unknown_state"
