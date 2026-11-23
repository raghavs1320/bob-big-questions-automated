"""Word-level timing and temporal alignment engine for kinetic subtitles."""

from typing import List, Optional
from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """Represents a single spoken word and its exact start/end timestamps."""
    word: str
    start_sec: float = Field(ge=0.0)
    end_sec: float = Field(ge=0.0)


def extract_word_timing(
    text: str,
    total_duration_sec: float,
    word_boundaries: Optional[List[dict]] = None,
) -> List[WordTimestamp]:
    """Generates millisecond-accurate word timestamps for subtitle animation."""
    words = [w.strip() for w in text.split() if w.strip()]
    if not words:
        return []

    # If external TTS boundary markers are provided, use them
    if word_boundaries and len(word_boundaries) >= len(words):
        result = []
        for b in word_boundaries:
            w_text = b.get("text", "")
            s_time = float(b.get("offset", 0.0)) / 10_000_000.0  # Convert 100ns units to sec
            d_time = float(b.get("duration", 0.0)) / 10_000_000.0
            result.append(
                WordTimestamp(
                    word=w_text,
                    start_sec=round(s_time, 3),
                    end_sec=round(s_time + d_time, 3),
                )
            )
        return result

    # Character-weighted duration interpolation
    # Longer words and words ending with punctuation take proportionally longer to pronounce
    weights = []
    for w in words:
        char_weight = max(1.0, float(len(w)))
        if w.endswith((".", "!", "?", ",", ";")):
            char_weight += 1.5  # Natural pause after punctuation
        weights.append(char_weight)

    total_weight = sum(weights)
    current_time = 0.0
    result: List[WordTimestamp] = []

    for word, weight in zip(words, weights):
        duration = (weight / total_weight) * total_duration_sec
        start = current_time
        end = current_time + duration
        result.append(
            WordTimestamp(
                word=word,
                start_sec=round(start, 3),
                end_sec=round(end, 3),
            )
        )
        current_time = end

    return result

