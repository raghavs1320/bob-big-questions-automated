"""Simple, human-readable logging with clear status icons."""

import sys
from datetime import datetime


class SimpleLogger:
    """A clean logger that prints friendly messages without messy jargon."""

    def __init__(self, name: str = "Studio"):
        self.name = name

    def _format(self, symbol: str, category: str, message: str) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {symbol} [{self.name}] {message}"

    def info(self, message: str) -> None:
        """General information step."""
        print(self._format("ℹ️", "INFO", message))

    def search(self, message: str) -> None:
        """Finding or scanning clips."""
        print(self._format("🔍", "SEARCH", message))

    def ai(self, message: str) -> None:
        """AI watching, analyzing, or writing."""
        print(self._format("🧠", "AI", message))

    def voice(self, message: str) -> None:
        """Voice recording step."""
        print(self._format("🎙️", "VOICE", message))

    def edit(self, message: str) -> None:
        """Video editing / cutting / rendering."""
        print(self._format("✂️", "EDIT", message))

    def success(self, message: str) -> None:
        """Step successfully completed."""
        print(self._format("✅", "SUCCESS", message))

    def warn(self, message: str) -> None:
        """Warning / clip skipped / filtered."""
        print(self._format("⚠️", "WARNING", message), file=sys.stderr)

    def error(self, message: str) -> None:
        """Something went wrong."""
        print(self._format("❌", "ERROR", message), file=sys.stderr)


# Default studio logger instance
logger = SimpleLogger("DailyDose")

