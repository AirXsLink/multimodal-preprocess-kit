"""Default no-borrow policy tests."""

from mm_preprocess_kit.fallback import can_borrow_other_media
from mm_preprocess_kit.models import MediaItem, PolicyConfig


def test_borrow_is_disabled_by_default() -> None:
    media = MediaItem(id="img", kind="image")
    assert can_borrow_other_media(media, PolicyConfig()) is False
