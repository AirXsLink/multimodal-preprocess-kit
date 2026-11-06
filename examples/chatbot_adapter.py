"""Example adapter: turn a media item into a delivery decision.

Run from the project root after an editable install:

    python examples/chatbot_adapter.py

The script uses in-memory fake data only; it never touches the network or disk.
"""

from mm_preprocess_kit.fallback import can_use_thumbnail
from mm_preprocess_kit.models import MediaItem, PolicyConfig
from mm_preprocess_kit.policy import choose_caption_mode, decide


def plan_delivery(media: MediaItem, now: float, cfg: PolicyConfig) -> str:
    """Map a decision to a one-line instruction for a caller."""
    decision = decide(media, now, cfg)

    if decision.action == "defer":
        return "wait {:.1f}s, then evaluate again".format(decision.retry_after or 0.0)
    if decision.action == "retry_caption":
        return "request a new caption"
    if decision.action == "push_now":
        if decision.caption_mode == "auto":
            # The adapter owns image sizing; here the fake screenshot is 1600x2400.
            mode = choose_caption_mode(1600, 2400, cfg)
            return "push with caption ({})".format(mode)
        return "push with caption"
    if decision.action == "push_without_media":
        if can_use_thumbnail(media, cfg):
            return "push with thumbnail fallback"
        return "push text only"
    return "drop media"


def main() -> None:
    cfg = PolicyConfig()
    now = 30.0
    samples = [
        MediaItem(id="s1", kind="image", caption_status="pending", received_at=0.0),
        MediaItem(id="s2", kind="screenshot", caption="x" * 60, caption_status="ready"),
        MediaItem(id="s3", kind="image", caption_status="failed"),
    ]

    for media in samples:
        decision = decide(media, now, cfg)
        print(
            "{id}: {action}/{reason} -> {plan}".format(
                id=media.id,
                action=decision.action,
                reason=decision.reason,
                plan=plan_delivery(media, now, cfg),
            )
        )


if __name__ == "__main__":
    main()
