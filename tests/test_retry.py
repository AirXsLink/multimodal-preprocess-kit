"""Caption retry threshold tests."""

from mm_preprocess_kit.models import PolicyConfig
from mm_preprocess_kit.policy import should_retry_caption


def test_short_caption_needs_retry() -> None:
    assert should_retry_caption("x" * 35, PolicyConfig()) is True


def test_long_caption_does_not_need_retry() -> None:
    assert should_retry_caption("x" * 50, PolicyConfig()) is False
