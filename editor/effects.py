"""Visual effects: aspect ratio normalization, punchline micro-zooms, and creator badges."""

from typing import Tuple


def build_aspect_ratio_filter(target_ratio: str = "16:9") -> Tuple[int, int, str]:
    """Generates FFmpeg filter for fitting any video into target aspect ratio with blurred canvas.

    Returns:
        (target_width, target_height, filter_string)
    """
    if target_ratio == "9:16":
        tw, th = 1080, 1920
    else:
        tw, th = 1920, 1080

    # Clean scaling with centered placement
    # Split input: [0:v] split [bg][fg];
    # [bg] scale=tw:th,boxblur=20 [bg_blur];
    # [fg] scale=tw:th:force_original_aspect_ratio=decrease [fg_scaled];
    # [bg_blur][fg_scaled] overlay=(W-w)/2:(H-h)/2
    filter_graph = (
        f"split[bg][fg];"
        f"[bg]scale={tw}:{th},boxblur=25[bg_blur];"
        f"[fg]scale={tw}:{th}:force_original_aspect_ratio=decrease[fg_scaled];"
        f"[bg_blur][fg_scaled]overlay=(W-w)/2:(H-h)/2,setsar=1"
    )
    return tw, th, filter_graph


def build_punchline_zoom_filter(punchline_sec: float, duration_sec: float) -> str:
    """Builds an FFmpeg filter that applies a 1.15x micro-zoom on the punchline."""
    if punchline_sec <= 0 or punchline_sec >= duration_sec:
        return ""

    start_zoom = max(0.0, punchline_sec - 0.2)
    end_zoom = min(duration_sec, punchline_sec + 1.2)

    # 1.15x scale and center crop enabled only during punchline window
    zoom_filter = (
        f"scale=iw*1.15:ih*1.15:eval=init,"
        f"crop=in_w/1.15:in_h/1.15:(in_w-in_w/1.15)/2:(in_h-in_h/1.15)/2:enable='between(t,{start_zoom:.2f},{end_zoom:.2f})'"
    )
    return zoom_filter


def build_credit_badge_filter(credit_text: str, target_ratio: str = "16:9") -> str:
    """Builds an on-screen attribution badge in the corner."""
    if not credit_text:
        return ""

    clean_text = credit_text.replace(":", "\\:").replace("'", "").replace('"', "")
    font_size = 32 if target_ratio == "9:16" else 26
    y_pos = "H-th-50" if target_ratio == "16:9" else "H-th-180"

    # drawtext with semi-transparent rounded box
    return (
        f"drawtext=text='{clean_text}':fontcolor=white@0.95:fontsize={font_size}:"
        f"x=45:y={y_pos}:box=1:boxcolor=black@0.45:boxborderw=8"
    )

