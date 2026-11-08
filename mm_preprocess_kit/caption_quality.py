"""Heuristics for judging whether a caption is usable.

Every function here is pure: no model calls, no filesystem, no network. The
heuristics encode three failure modes observed in production:

1. **placeholder-only captions** - the model writes ``□`` for every glyph it
   cannot read. A length check passes because the placeholder is a character.
2. **prompt echo** - the model copies the instruction back instead of
   describing the image.
3. **too-short captions** - a text-heavy image gets a caption like ``21:30``.

The heuristics are deliberately conservative. Rejecting a good caption costs
one retry; accepting a bad caption puts garbage into the conversation context,
where the model then answers based on it.
"""

from dataclasses import dataclass, field
from typing import Optional

#: Characters that vision models use for glyphs they cannot read.
PLACEHOLDER_CHARS = frozenset("□■▢▣◻◼◾▪▫�")

#: Instruction phrases that, when copied back, indicate prompt echo.
#: Defaults cover the Chinese and English transcription prompts this kit was
#: extracted from; pass your own list for a different prompt.
DEFAULT_ECHO_PHRASES: tuple[str, ...] = (
    "逐行原样抄写",
    "不要总结",
    "不要漏行",
    "看不清的字用",
    "没有文字就只描述画面",
    "不要逐行抄写",
    "保留换行",
    "直接用一句话说明画面",
    "不要复述要求本身",
    "transcribe every line",
    "do not summarize",
    "do not skip",
    "unreadable characters",
    "keep line breaks",
)


@dataclass
class CaptionQualityConfig:
    """Thresholds for the caption-quality heuristics."""

    #: Captions with fewer meaningful characters are treated as unusable.
    min_meaningful_chars: int = 3
    #: A caption needs at least this many placeholders before density matters.
    placeholder_min_count: int = 4
    #: Placeholders must outnumber meaningful characters by this factor.
    placeholder_ratio: float = 2.0
    #: How many distinct echo phrases count as a prompt echo.
    echo_min_hits: int = 2
    #: Phrases that indicate the model copied the instruction back.
    echo_phrases: tuple[str, ...] = field(default=DEFAULT_ECHO_PHRASES)


@dataclass
class CaptionAssessment:
    """The result of assessing one caption.

    ``issue`` is ``None`` when the caption is usable, otherwise one of
    ``"empty"``, ``"too_short"``, ``"placeholder"`` or ``"prompt_echo"``.
    The counts are kept so callers can log *why* a caption was rejected.
    """

    usable: bool
    issue: Optional[str]
    meaningful_chars: int
    placeholder_chars: int
    echo_hits: int


def count_meaningful(text: Optional[str]) -> int:
    """Count alphanumeric characters, ignoring whitespace and punctuation."""
    if not text:
        return 0
    return sum(1 for char in text if char.isalnum())


def count_placeholders(text: Optional[str]) -> int:
    """Count placeholder glyphs such as ``□``."""
    if not text:
        return 0
    return sum(1 for char in text if char in PLACEHOLDER_CHARS)


def count_echo_hits(text: str, cfg: CaptionQualityConfig) -> int:
    """Count how many distinct echo phrases appear in ``text``."""
    lowered = text.casefold()
    return sum(1 for phrase in cfg.echo_phrases if phrase.casefold() in lowered)


def assess_caption(
    caption: Optional[str], cfg: Optional[CaptionQualityConfig] = None
) -> CaptionAssessment:
    """Assess a caption and return the verdict plus its evidence."""
    cfg = cfg or CaptionQualityConfig()
    text = caption or ""
    meaningful = count_meaningful(text)
    placeholders = count_placeholders(text)
    echo_hits = count_echo_hits(text, cfg) if text else 0

    def verdict(issue: Optional[str]) -> CaptionAssessment:
        return CaptionAssessment(
            usable=issue is None,
            issue=issue,
            meaningful_chars=meaningful,
            placeholder_chars=placeholders,
            echo_hits=echo_hits,
        )

    if not text.strip():
        return verdict("empty")

    # A caption made only of placeholders is a placeholder caption, not a
    # short one; report the more specific reason.
    if placeholders >= cfg.placeholder_min_count and meaningful == 0:
        return verdict("placeholder")

    if meaningful < cfg.min_meaningful_chars:
        return verdict("too_short")

    if placeholders >= cfg.placeholder_min_count and placeholders > meaningful * cfg.placeholder_ratio:
        return verdict("placeholder")

    if echo_hits >= cfg.echo_min_hits:
        return verdict("prompt_echo")

    return verdict(None)


def is_usable(
    caption: Optional[str], cfg: Optional[CaptionQualityConfig] = None
) -> bool:
    """Return True when a caption is worth injecting into the context."""
    return assess_caption(caption, cfg).usable
