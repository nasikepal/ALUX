#!/usr/bin/env python3
"""
ALUX Production OS — one-shot setup for a new machine (macOS or Windows).

    python3 setup/install.py            # install whatever is missing, then print the checklist
    python3 setup/install.py --check    # only report, change nothing
    python3 setup/install.py --only models,bridge
    python3 setup/install.py --fonts "/path/to/Gilroy_fixed (INSTALL INI)"

Every step is idempotent: what is already installed is left alone. Standard library only, so it runs before
the project's .venv exists. Steps a script cannot do (sign-ins, importing Figma plugins, opening the Premiere
panel) are printed at the end as a checklist.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
MAC = sys.platform == "darwin"
WIN = os.name == "nt"
ALUX_BIN = HOME / ".alux" / "bin"
MODELS_DIR = HOME / ".cache" / "whisper"
BRIDGE_SRC = ROOT / "08_AUTOMATION" / "premiere-bridge"
BRIDGE_ID = "com.feugee.claudebridge"
BRIDGE_DATA = HOME / "Library" / "Application Support" / "ClaudeBridge"   # same path on Windows (the panel uses os.homedir())
FONT_FOLDER_NAME = "Gilroy_fixed (INSTALL INI)"
FONTS = ["Gilroy-Light", "Gilroy-Regular", "Gilroy-Medium", "Gilroy-Bold", "Gilroy-Heavy"]

# name -> (brew formula, winget id)
TOOLS = {
    "git": ("git", "Git.Git"),
    "ffmpeg": ("ffmpeg", "Gyan.FFmpeg"),
    "magick": ("imagemagick", "ImageMagick.ImageMagick"),
    "gh": ("gh", "GitHub.cli"),
    "uv": ("uv", "astral-sh.uv"),
    "whisper-cli": ("whisper-cpp", None),          # Windows: prebuilt zip from the whisper.cpp releases
}
MODELS = {  # file -> minimum plausible size in bytes (a truncated download is re-fetched)
    "ggml-large-v3-turbo.bin": 1_500_000_000,
    "ggml-base.en.bin": 140_000_000,
}
MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{}"

OK, MISSING, MANUAL = "ok", "missing", "manual"
report = []          # (component, status, detail)
todo = []            # manual steps printed at the end


def say(msg):
    print(f"  · {msg}", flush=True)


def run(cmd, **kw):
    say(" ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=False, **kw)


def which(name):
    exe = name + (".exe" if WIN else "")
    found = shutil.which(name) or shutil.which(exe)
    if found:
        return found
    local = ALUX_BIN / exe
    return str(local) if local.exists() else None


def record(component, status, detail=""):
    report.append((component, status, detail))


# ------------------------------------------------------------------------------------------------ tools
def step_tools(check):
    if MAC and not shutil.which("brew"):
        record("homebrew", MISSING, "install from https://brew.sh, then re-run")
        todo.append("Install Homebrew (https://brew.sh) and run this installer again.")
        return
    if WIN and not shutil.which("winget"):
        record("winget", MISSING, "update 'App Installer' from the Microsoft Store")
        todo.append("Install/update 'App Installer' (winget) from the Microsoft Store, then re-run.")
        return
    for name, (formula, winget_id) in TOOLS.items():
        path = which(name)
        if path:
            record(name, OK, path)
            continue
        if check:
            record(name, MISSING)
            continue
        if MAC:
            run(["brew", "install", formula])
        elif WIN and winget_id:
            run(["winget", "install", "-e", "--id", winget_id, "--accept-source-agreements", "--accept-package-agreements"])
        elif WIN and name == "whisper-cli":
            install_whisper_windows()
        path = which(name)
        record(name, OK if path else MISSING, path or "install failed — see output above")
        if WIN and not path and name != "whisper-cli":
            todo.append(f"{name}: open a NEW terminal (winget updates PATH only for new shells) and re-run --check.")


def install_whisper_windows():
    """Latest whisper.cpp release, prebuilt x64 binaries, into ~/.alux/bin."""
    api = "https://api.github.com/repos/ggml-org/whisper.cpp/releases/latest"
    with urllib.request.urlopen(api, timeout=30) as r:
        release = json.load(r)
    asset = next((a for a in release["assets"] if a["name"] == "whisper-bin-x64.zip"), None)
    if not asset:
        say("no whisper-bin-x64.zip in the latest release — build whisper.cpp manually")
        return
    ALUX_BIN.mkdir(parents=True, exist_ok=True)
    zpath = ALUX_BIN / asset["name"]
    download(asset["browser_download_url"], zpath)
    with zipfile.ZipFile(zpath) as z:
        for member in z.namelist():
            if member.lower().endswith((".exe", ".dll")):
                (ALUX_BIN / Path(member).name).write_bytes(z.read(member))
    zpath.unlink()


# ------------------------------------------------------------------------------------------------ python
def step_python(check):
    ok = sys.version_info >= (3, 10)
    record("python", OK if ok else MISSING, platform.python_version() + ("" if ok else " (need 3.10+)"))
    venv_py = ROOT / ".venv" / ("Scripts/python.exe" if WIN else "bin/python")
    if venv_py.exists() and deps_ok(venv_py):
        record(".venv", OK, str(venv_py))
        return
    if check:
        record(".venv", MISSING)
        return
    uv = which("uv")
    if uv:
        run([uv, "venv", str(ROOT / ".venv")], cwd=ROOT)
        run([uv, "pip", "install", "--python", str(venv_py), "-r", str(ROOT / "requirements.txt")], cwd=ROOT)
    else:
        run([sys.executable, "-m", "venv", str(ROOT / ".venv")])
        run([str(venv_py), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    record(".venv", OK if deps_ok(venv_py) else MISSING, str(venv_py))


def deps_ok(venv_py):
    r = subprocess.run([str(venv_py), "-c", "import docx, yaml, requests, rich"], capture_output=True)
    return r.returncode == 0


# ------------------------------------------------------------------------------------------------ models
def download(url, dest):
    tmp = dest.with_suffix(dest.suffix + ".part")
    say(f"download {url}")
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done, last = 0, 0.0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if total and time.time() - last > 2:
                print(f"    {done / total:6.1%}  {done >> 20} / {total >> 20} MB", flush=True)
                last = time.time()
    tmp.replace(dest)


def step_models(check):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, min_size in MODELS.items():
        path = MODELS_DIR / name
        if path.exists() and path.stat().st_size >= min_size:
            record(f"model {name}", OK, str(path))
            continue
        if check:
            record(f"model {name}", MISSING, str(path))
            continue
        download(MODEL_URL.format(name), path)
        good = path.exists() and path.stat().st_size >= min_size
        record(f"model {name}", OK if good else MISSING, str(path))


# ------------------------------------------------------------------------------------------------ premiere bridge
def cep_dir():
    if MAC:
        return HOME / "Library" / "Application Support" / "Adobe" / "CEP" / "extensions"
    return Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming")) / "Adobe" / "CEP" / "extensions"


def debug_mode_on():
    """Unsigned CEP panels (like Claude Bridge) only load with PlayerDebugMode=1."""
    for v in range(9, 14):
        if MAC:
            r = subprocess.run(["defaults", "read", f"com.adobe.CSXS.{v}", "PlayerDebugMode"], capture_output=True, text=True)
            if r.stdout.strip() != "1":
                return False
        elif WIN:
            r = subprocess.run(["reg", "query", rf"HKCU\Software\Adobe\CSXS.{v}", "/v", "PlayerDebugMode"], capture_output=True, text=True)
            if "0x1" not in r.stdout and " 1" not in r.stdout:
                return False
    return True


def step_bridge(check):
    dest = cep_dir() / BRIDGE_ID
    same = dest.exists() and all((dest / p).exists() and (dest / p).read_bytes() == (BRIDGE_SRC / p).read_bytes()
                                  for p in ("index.html", "CSXS/manifest.xml"))
    if not same and not check:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(BRIDGE_SRC, dest, dirs_exist_ok=True)
        same = True
    record("premiere bridge panel", OK if same else MISSING, str(dest))

    debug = debug_mode_on()
    if not debug and not check:
        for v in range(9, 14):
            if MAC:
                run(["defaults", "write", f"com.adobe.CSXS.{v}", "PlayerDebugMode", "1"])
            elif WIN:
                run(["reg", "add", rf"HKCU\Software\Adobe\CSXS.{v}", "/v", "PlayerDebugMode", "/t", "REG_SZ", "/d", "1", "/f"],
                    capture_output=True)
        debug = debug_mode_on()
    record("CEP PlayerDebugMode", OK if debug else MISSING, "CSXS 9–13")

    for d in (BRIDGE_DATA / "inbox", BRIDGE_DATA / "outbox"):
        if not check:
            d.mkdir(parents=True, exist_ok=True)
    if MAC and not check:
        shutil.copy2(BRIDGE_SRC / "ppro.sh", BRIDGE_DATA / "ppro.sh")
        os.chmod(BRIDGE_DATA / "ppro.sh", 0o755)

    premiere = list(Path("/Applications").glob("Adobe Premiere Pro*")) if MAC else \
        list(Path(os.environ.get("ProgramFiles", r"C:\Program Files"), "Adobe").glob("Adobe Premiere Pro*"))
    record("Adobe Premiere Pro", OK if premiere else MISSING, premiere[0].name if premiere else "install via Creative Cloud")
    todo.append("Premiere: restart it, then Window > Extensions > Claude Bridge. The panel must say 'connected'.")


# ------------------------------------------------------------------------------------------------ fonts
def font_dir():
    if MAC:
        return HOME / "Library" / "Fonts"
    return Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local")) / "Microsoft" / "Windows" / "Fonts"


def fonts_installed():
    dirs = [font_dir()] + ([Path("/Library/Fonts")] if MAC else [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"])
    return all(any((d / f"{f}.{ext}").exists() for d in dirs for ext in ("ttf", "otf")) for f in FONTS)


def find_font_source(explicit):
    if explicit:
        return Path(explicit)
    if os.environ.get("ALUX_FONTS"):
        return Path(os.environ["ALUX_FONTS"])
    roots = list((HOME / "Library" / "CloudStorage").glob("GoogleDrive-*")) if MAC else \
        [Path(f"{d}:\\") for d in "GHIJ" if Path(f"{d}:\\My Drive").exists()] + [HOME / "Google Drive"]
    deadline = time.time() + 30          # Drive folders stream from the network: never walk them forever
    for root in roots:
        for dirpath, dirnames, _ in os.walk(root):
            if Path(dirpath).name == FONT_FOLDER_NAME:
                return Path(dirpath)
            if time.time() > deadline or len(Path(dirpath).relative_to(root).parts) >= 5:
                dirnames[:] = []
    return None


def step_fonts(check, explicit):
    if fonts_installed():
        record("fonts Gilroy (fixed)", OK, str(font_dir()))
        return
    if check:
        record("fonts Gilroy (fixed)", MISSING)
        todo.append(f"Fonts: run with --fonts \"<Drive>/…/{FONT_FOLDER_NAME}\" (licensed, not in this public repo).")
        return
    src = find_font_source(explicit)
    files = [p for p in (src.rglob("*") if src and src.exists() else []) if p.suffix.lower() in (".ttf", ".otf")]
    if not files:
        record("fonts Gilroy (fixed)", MISSING, f"folder '{FONT_FOLDER_NAME}' not found")
        todo.append(f"Fonts: make the Drive folder '{FONT_FOLDER_NAME}' available offline, then re-run with --fonts \"<path>\".")
        return
    dest = font_dir()
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, dest / f.name)
        if WIN:   # per-user font registration so apps see it without a reboot
            run(["reg", "add", r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts", "/v",
                 f"{f.stem} (TrueType)", "/t", "REG_SZ", "/d", str(dest / f.name), "/f"], capture_output=True)
    record("fonts Gilroy (fixed)", OK if fonts_installed() else MISSING, f"{len(files)} files from {src}")
    todo.append("Fonts: restart Premiere, After Effects and Figma so they pick up Gilroy.")


# ------------------------------------------------------------------------------------------------ figma + claude
def step_figma(check):
    figma = Path("/Applications/Figma.app").exists() if MAC else \
        (Path(os.environ.get("LOCALAPPDATA", "")) / "Figma").exists()
    record("Figma desktop", OK if figma else MISSING, "" if figma else "https://www.figma.com/downloads/")
    record("Figma MCP (.mcp.json)", OK if (ROOT / ".mcp.json").exists() else MISSING, "project-scoped, loads in Claude Code")
    plugins = sorted((ROOT / "08_AUTOMATION" / "figma-plugins").glob("*/manifest.json"))
    todo.append("Figma MCP: in Claude Code run /mcp → figma → Authenticate (once per machine).")
    todo.append("Figma plugins: Figma desktop → Plugins → Development → Import plugin from manifest…, pick each:\n"
                + "\n".join(f"        {p}" for p in plugins)
                + "\n     alux-fill-map/code.js is generated per episode (client data, never committed):"
                  "\n        .venv/bin/python 08_AUTOMATION/Scripts/episode/figma_fill.py <episode folder>")
    claude = which("claude")
    record("Claude Code CLI", OK if claude else MANUAL, claude or "optional; the desktop app works too")
    gh = which("gh")
    if gh:
        r = subprocess.run([gh, "auth", "status"], capture_output=True, text=True)
        record("GitHub login", OK if r.returncode == 0 else MISSING, "" if r.returncode == 0 else "run: gh auth login")
        if r.returncode:
            todo.append("GitHub: gh auth login (needs contributor access to nasikepal/ALUX).")


# ------------------------------------------------------------------------------------------------ main
STEPS = ["tools", "python", "models", "bridge", "fonts", "figma"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, install nothing")
    ap.add_argument("--only", help="comma list of: " + ",".join(STEPS))
    ap.add_argument("--fonts", help=f"path to the '{FONT_FOLDER_NAME}' folder")
    args = ap.parse_args()
    if not (MAC or WIN):
        sys.exit("macOS and Windows only.")
    steps = args.only.split(",") if args.only else STEPS
    print(f"ALUX setup — {'check' if args.check else 'install'} on {platform.system()} ({ROOT})")
    for s in steps:
        print(f"\n[{s}]")
        if s == "tools":
            step_tools(args.check)
        elif s == "python":
            step_python(args.check)
        elif s == "models":
            step_models(args.check)
        elif s == "bridge":
            step_bridge(args.check)
        elif s == "fonts":
            step_fonts(args.check, args.fonts)
        elif s == "figma":
            step_figma(args.check)
        else:
            sys.exit(f"unknown step {s}")

    print("\n" + "=" * 72)
    width = max(len(c) for c, _, _ in report)
    for c, st, d in report:
        mark = {"ok": "✓", "missing": "✗", "manual": "…"}[st]
        print(f" {mark} {c.ljust(width)}  {d}")
    if todo:
        print("\nStill to do by hand:")
        for i, t in enumerate(dict.fromkeys(todo), 1):
            print(f" {i}. {t}")
    missing = [c for c, st, _ in report if st == MISSING]
    print(f"\n{'READY' if not missing else 'NOT READY — missing: ' + ', '.join(missing)}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
