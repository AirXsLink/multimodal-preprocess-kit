"""Safe fallback policies for media that cannot be delivered.

Both helpers are pure predicates. They never fetch, borrow or decode anything;
they only tell a caller which fallback is permitted by policy.
"""

from .models import MediaItem, PolicyConfig


def can_use_thumbnail(media: MediaItem, cfg: PolicyConfig) -> bool:
    """Return True when no local file exists and thumbnails are allowed."""
    return media.local_path is None and cfg.allow_thumbnail_fallback


def can_borrow_other_media(media: MediaItem, cfg: PolicyConfig) -> bool:
    """Return True only when the caller explicitly opts in to borrowing.

    Borrowing another message's media is unsafe by default: it can silently
    attach the wrong picture to a message. The default is therefore ``False``
    and must be opted into explicitly.
    """
    return cfg.allow_borrow_other_media is True
