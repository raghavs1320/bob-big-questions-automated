"""Native macOS desktop notifications for video completion and approval alerts."""

import platform
import subprocess
from utils.logger import logger


def send_macos_notification(title: str, message: str, subtitle: str = "") -> bool:
    """Displays a native macOS banner notification."""
    if platform.system() != "Darwin":
        return False

    clean_title = title.replace('"', '\\"')
    clean_msg = message.replace('"', '\\"')
    clean_sub = subtitle.replace('"', '\\"')

    script = f'display notification "{clean_msg}" with title "{clean_title}"'
    if clean_sub:
        script += f' subtitle "{clean_sub}"'

    try:
        subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        logger.warn(f"Could not trigger macOS notification: {e}")
        return False

