"""Caption quality heuristics: real misfires and their negative examples."""

from mm_preprocess_kit.caption_quality import (
    CaptionQualityConfig,
    assess_caption,
    count_meaningful,
    count_placeholders,
    is_usable,
)

# A real caption: the model read the drum-brand logo ("REM") and produced a
# placeholder for every other line.
PLACEHOLDER_CAPTION = "REM\n" + "\u25a1\n" * 32

# A real miss: the model copied the transcription instruction back.
PROMPT_ECHO_CAPTION = (
    "\u8fd9\u662f\u4e00\u5f20\u53ef\u80fd\u5305\u542b\u6587\u5b57\u7684\u56fe"
    "\uff08\u622a\u56fe/\u7167\u7247\uff09\u3002\u8bf7\u5148\u9010\u884c\u539f"
    "\u6837\u6284\u5199\u56fe\u4e2d\u6240\u6709\u53ef\u89c1\u6587\u5b57\uff0c"
    "\u4fdd\u7559\u6362\u884c\uff0c\u4e0d\u8981\u603b\u7ed3\u3001\u4e0d\u8981\u6f0f"
    "\u884c\uff1b\u770b\u4e0d\u6e05\u7684\u5b57\u7528 \u25a1 \u4ee3\u66ff\u3002"
)


def test_empty_caption_is_empty() -> None:
    assert assess_caption("").issue == "empty"
    assert is_usable("") is False


def test_whitespace_caption_is_empty() -> None:
    assert assess_caption("   \n\t").issue == "empty"


def test_placeholder_only_caption_is_placeholder() -> None:
    assert assess_caption("\u25a1" * 4).issue == "placeholder"


def test_placeholder_density_rejects_a_real_caption() -> None:
    assessment = assess_caption(PLACEHOLDER_CAPTION)
    assert assessment.usable is False
    assert assessment.issue == "placeholder"
    assert assessment.meaningful_chars == 3
    assert assessment.placeholder_chars == 32


def test_single_placeholder_is_too_short() -> None:
    assert assess_caption("\u25a1").issue == "too_short"


def test_one_character_caption_is_too_short() -> None:
    assert assess_caption("\u95e8").issue == "too_short"


def test_clock_caption_is_usable() -> None:
    # "21:30" is short but has four alphanumeric characters; the length-retry
    # policy (min_caption_chars) is a separate layer.
    assert is_usable("21:30") is True


def test_normal_chinese_caption_is_usable() -> None:
    assert is_usable("\u8fd9\u662f\u4e00\u5f20\u96ea\u666f\u7167\u7247\uff0c\u6811\u6728\u8986\u76d6\u7740\u767d\u96ea\u3002") is True


def test_prompt_echo_is_rejected() -> None:
    assessment = assess_caption(PROMPT_ECHO_CAPTION)
    assert assessment.usable is False
    assert assessment.issue == "prompt_echo"
    assert assessment.echo_hits >= 2


def test_single_echo_phrase_is_not_rejected() -> None:
    # A single phrase may legitimately appear in the image itself.
    assert is_usable("\u8bf7\u5148\u9010\u884c\u539f\u6837\u6284\u5199") is True


def test_english_prompt_echo_is_rejected() -> None:
    caption = "Transcribe every line exactly. Do not summarize. Keep line breaks."
    assert assess_caption(caption).issue == "prompt_echo"


def test_assessment_reports_evidence() -> None:
    assessment = assess_caption(PLACEHOLDER_CAPTION)
    assert assessment.meaningful_chars == 3
    assert assessment.placeholder_chars == 32
    assert assessment.echo_hits == 0


def test_custom_echo_phrases() -> None:
    cfg = CaptionQualityConfig(echo_phrases=("foo", "bar"))
    assert assess_caption("foo bar", cfg).issue == "prompt_echo"
    assert assess_caption("foo only", cfg).usable is True


def test_few_placeholders_below_ratio_is_usable() -> None:
    # "REM" plus four placeholders: 4 is not greater than 3 * 2.
    caption = "REM\n" + "\u25a1\n" * 4
    assert is_usable(caption) is True


def test_counts_ignore_punctuation() -> None:
    assert count_meaningful("\u4f60\u597d\uff0c\u4e16\u754c\uff01") == 4
    assert count_placeholders("\u25a1\u25a0\u25a1") == 3
