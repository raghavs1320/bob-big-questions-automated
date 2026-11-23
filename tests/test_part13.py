"""Test suite for Part 13: Modern Web Studio Dashboard."""

import py_compile
from pathlib import Path
import pytest
from ui.style import PURE_WHITE_CSS


def test_pure_white_css_styling():
    """Verify CSS incorporates pure white background, custom typography, and pill buttons."""
    assert "#FFFFFF" in PURE_WHITE_CSS
    assert "-apple-system" in PURE_WHITE_CSS
    assert "border-radius: 9999px" in PURE_WHITE_CSS  # Pill button
    assert "visibility: hidden" in PURE_WHITE_CSS  # Hides default Streamlit menu


def test_ui_python_scripts_syntax():
    """Verify all UI scripts compile cleanly without any syntax errors."""
    scripts = [
        Path("ui/style.py"),
        Path("ui/dashboard.py"),
        Path("run_studio.py"),
    ]
    for script in scripts:
        assert script.exists(), f"Missing UI script: {script}"
        # py_compile will raise PyCompileError if there are any syntax errors
        py_compile.compile(str(script), doraise=True)

