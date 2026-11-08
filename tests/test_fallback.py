"""Thumbnail and borrow fallback tests."""

from mm_preprocess_kit.fallback import can_borrow_other_media, can_use_thumbnail
from mm_preprocess_kit.models import MediaItem, PolicyConfig


def test_missing_local_path_allows_thumbnail() -> None:
    media = MediaItem(id="img", kind="image", local_path=None)
    assert can_use_thumbnail(media, PolicyConfig(allow_thumbnail_fallback=True)) is True


def test_thumbnail_fallback_can_be_disabled() -> None:
    media = MediaItem(id="img", kind="image", local_path=None)
    assert can_use_thumbnail(media, PolicyConfig(allow_thumbnail_fallback=False)) is False


def test_borrow_can_be_opted_in() -> None:
    media = MediaItem(id="img", kind="image")
    assert can_borrow_other_media(media, PolicyConfig(allow_borrow_other_media=True)) is True
