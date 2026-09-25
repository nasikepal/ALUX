"""Where the external binaries live. setup/install.py puts anything it cannot get from a package manager in ~/.alux/bin."""

import os
import shutil
from pathlib import Path

ALUX_HOME = Path.home() / ".alux"
WHISPER_MODELS = Path.home() / ".cache" / "whisper"


def binary(name: str) -> str:
    exe = name + (".exe" if os.name == "nt" else "")
    found = shutil.which(name) or shutil.which(exe)
    if found:
        return found
    local = ALUX_HOME / "bin" / exe
    return str(local) if local.exists() else name


WHISPER = binary("whisper-cli")
