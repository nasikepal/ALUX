"""
Logging module for the Obsidian Production OS using rich and persistent file logs.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Enforce UTF-8 on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.logging import RichHandler

console = Console(force_terminal=True, legacy_windows=False)

LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "08_AUTOMATION" / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_filename = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True, show_time=False),
        logging.FileHandler(log_filename, encoding="utf-8")
    ]
)

logger = logging.getLogger("production_os")
