"""Thumbnail fallback tests."""

from mm_preprocess_kit.fallback import can_use_thumbnail
from mm_preprocess_kit.models import MediaItem, PolicyConfig


def test_missing_local_path_allows_thumbnail() -> None:
    media = MediaItem(id="img", kind="image", local_path=None)
    assert can_use_thumbnail(media, PolicyConfig(allow_thumbnail_fallback=True)) is True
