"""Audio ducking engine: lowers video background sound during narrator voiceover."""

from typing import Tuple


def build_audio_ducking_filter(voice_duration_sec: float) -> str:
    """Builds an FFmpeg audio filter that ducks video audio to 15% during voiceover.

    Args:
        voice_duration_sec: Duration in seconds of the narrator voiceover track.

    Returns:
        FFmpeg complex filter graph string for audio mixing.
    """
    safe_dur = max(0.5, voice_duration_sec)

    # 1. Video original audio [0:a] is ducked to 15% while voiceover speaks (0 to safe_dur)
    # 2. Voiceover [1:a] plays at full volume
    # 3. Both are mixed cleanly together
    filter_graph = (
        f"[0:a]volume=enable='between(t,0,{safe_dur:.2f})':volume=0.15[ducked_bg];"
        f"[ducked_bg][1:a]amix=inputs=2:duration=first:dropout_transition=1[aout]"
    )
    return filter_graph

