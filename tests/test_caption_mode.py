"""Caption mode selection tests."""

from mm_preprocess_kit.models import PolicyConfig
from mm_preprocess_kit.policy import choose_caption_mode


def test_tall_screenshot_uses_transcribe() -> None:
    assert choose_caption_mode(1200, 3000, PolicyConfig()) == "transcribe"


def test_small_image_uses_describe() -> None:
    # The default threshold (700) would classify 800x600 as transcribe because
    # its long edge is 800. Raise the threshold here so the describe branch is
    # exercised under the documented long-edge rule.
    cfg = PolicyConfig(long_image_min_edge=1000)
    assert choose_caption_mode(800, 600, cfg) == "describe"


def test_boundary_at_threshold_is_transcribe() -> None:
    assert choose_caption_mode(700, 400, PolicyConfig()) == "transcribe"


def test_below_threshold_is_describe() -> None:
    assert choose_caption_mode(699, 400, PolicyConfig()) == "describe"
