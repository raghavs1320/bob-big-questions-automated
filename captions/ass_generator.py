"""Advanced SubStation Alpha (.ass) kinetic animated subtitle compiler."""

from pathlib import Path
from typing import List
from captions.timing import WordTimestamp


def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS timestamp format (H:MM:SS.cc)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def generate_ass_subtitles(
    words: List[WordTimestamp],
    output_path: str,
    aspect_ratio: str = "16:9",
    words_per_phrase: int = 4,
) -> str:
    """Generates an animated .ass subtitle file with word-by-word karaoke yellow highlighting.

    Args:
        words: List of WordTimestamp objects.
        output_path: Target .ass file path.
        aspect_ratio: '16:9' or '9:16' (adjusts font size and vertical alignment).
        words_per_phrase: How many words to display on screen at once (3-4 is optimal).

    Returns:
        Absolute path to the created .ass file.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Resolution & Typography configuration
    if aspect_ratio == "9:16":
        res_x, res_y = 1080, 1920
        font_size = 72
        margin_v = 700  # Centered lower-middle for vertical Shorts
    else:
        res_x, res_y = 1920, 1080
        font_size = 54
        margin_v = 85  # Clean bottom-center for horizontal 16:9 YouTube

    # ASS Header & Styles
    # Primary color: White (&H00FFFFFF), Outline: Thick Black (&H00000000)
    header = f"""[Script Info]
Title: Daily Dose Kinetic Captions
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {res_x}
PlayResY: {res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines: List[str] = []

    # Group words into short 3-4 word phrases
    chunks = [words[i : i + words_per_phrase] for i in range(0, len(words), words_per_phrase)]

    for chunk in chunks:
        # For each word in the chunk, generate an active highlight state
        for active_idx, target_word in enumerate(chunk):
            start_str = format_ass_time(target_word.start_sec)
            end_str = format_ass_time(target_word.end_sec)

            # Build phrase text: active word is highlighted in Vivid Yellow (\c&H0000FFFF&)
            phrase_parts = []
            for idx, w in enumerate(chunk):
                if idx == active_idx:
                    # Active word in bright yellow with extra pop
                    phrase_parts.append(r"{\c&H0000FFFF&}" + w.word + r"{\c&H00FFFFFF&}")
                else:
                    phrase_parts.append(w.word)

            full_line_text = " ".join(phrase_parts)
            line = f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{full_line_text}"
            dialogue_lines.append(line)

    full_content = header + "\n".join(dialogue_lines) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return str(output_path)

