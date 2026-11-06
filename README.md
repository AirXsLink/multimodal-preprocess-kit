# multimodal-preprocess-kit

A framework-agnostic policy kit for chatbot multimodal preprocessing: caption retry, pending-message deferral, and safe fallback.

**At a glance (defaults):**

| Situation | Decision |
| --- | --- |
| Caption `failed` | `drop_media` |
| Caption `too_short`, or `ready` and under 40 chars | `retry_caption` |
| Caption `pending`, waited ≤ 90s | `defer` with `retry_after` |
| Caption `pending`, waited > 90s | `push_without_media` |
| Caption `ready` and non-empty | `push_now`; screenshots carry `"auto"` |
| No local file, thumbnails enabled | thumbnail fallback |
| Media from another message | never borrowed unless explicitly enabled |

## Problem

Vision-language captions are often slower than the chat message buffer. A bot may first answer that it cannot see an image, then describe it a second later. Screenshots lose their text when they are summarized instead of transcribed. And when the original media is unavailable, a pipeline may borrow a nearby image, silently attaching the wrong picture to a message.

## What it does NOT do

- Calls no model (VL, LLM, or otherwise).
- Connects to no chat platform and performs no network I/O.
- Stores no chat history.
- Reads, decodes, or uploads no media files.

## Install

```bash
pip install -e .
```

## Quick Start

```python
from mm_preprocess_kit.models import MediaItem, PolicyConfig
from mm_preprocess_kit.policy import decide

media = MediaItem(id="m1", kind="image", caption_status="pending", received_at=0.0)
decision = decide(media, now=30.0, cfg=PolicyConfig())
print(decision.action, decision.reason, decision.retry_after)  # defer caption_pending 60.0
```

Screenshots get `caption_mode="auto"`. Resolve it with `choose_caption_mode(width, height, cfg)` once your adapter knows the real pixel size.

## Policy Config Table

| Field | Default | Meaning |
| --- | --- | --- |
| `min_caption_chars` | 40 | Captions shorter than this (after trimming) are treated as missing. |
| `max_defer_seconds` | 90 | Upper bound on how long a pending message may be deferred. |
| `long_image_min_edge` | 700 | Long-edge threshold that selects `transcribe`. |
| `long_image_max_edge` | 1400 | Reserved for caller-side resizing. Not enforced in v0.1. |
| `long_image_max_tokens` | 900 | Reserved for caller-side budgeting. Not enforced in v0.1. |
| `allow_thumbnail_fallback` | True | Permit a thumbnail when no local file exists. |
| `allow_borrow_other_media` | False | Permit borrowing another message's media. Off by default. |

`long_image_min_edge` is a long-edge rule, not an area rule: an 800x600 image has a long edge of 800 and therefore selects `transcribe` at the default threshold.

## Design Decisions

**No borrowing by default.** A missing image is recoverable; a wrong image is not. Attaching another message's media can silently send someone else's picture, so it requires an explicit opt-in (`allow_borrow_other_media=True`).

**Prefer text over blocking.** When the deferral window expires, the message is pushed without media. Waiting longer delays every later message in the queue and produces inconsistent "no image" answers. The caption can still arrive later as a follow-up.

**Screenshots stay `auto` until the caller knows the size.** `decide` never learns an item's pixel size and never opens the file, so it returns `caption_mode="auto"`. The adapter resolves it with `choose_caption_mode(width, height, cfg)`.

**Where this kit deliberately stops.** A production adapter usually does more than these four functions. The gaps below are intentional, and each one changes how you should wire the kit:

- **Failure handling.** A real pipeline often pushes a placeholder ("media could not be described") instead of discarding the item. If yours does, map `caption_status="failed"` to `push_without_media`; reserve `drop_media` for pipelines that intentionally drop the item.
- **Garbage captions.** The retry rule is length-based only, so a caption made entirely of placeholders can still pass the 40-character check. Run your own "is this text meaningful" check before marking an item `ready`.
- **Text-heavy gating.** `should_retry_caption` applies to every caption. Production may retry only screenshots or long images; call it only for those kinds instead of unconditionally.
- **Thumbnail semantics.** `can_use_thumbnail` treats `local_path is None` as "no original is available". If the file exists but cannot be decoded, pass `None` rather than a path that will fail later.

This kit gives you the decision vocabulary; the adapter still owns these policy details.

## Test

```bash
pytest -q
```

## Compliance

This library contains only generic preprocessing policies. It does not include any platform automation implementation.

## License

MIT
