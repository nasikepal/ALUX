"""
ALUX episode pipeline — script + VO -> timeline.json -> Premiere.

Episode folder layout (one folder per episode):
    <episode>/material/   client .docx script + VO audio (as delivered)
    <episode>/build/      generated: words.json, timeline.json, marking.md, premiere_*.jsx
    <episode>/project/    Premiere project
    <episode>/assets/     footage & graphics for this episode

Usage (from the vault root):
    .venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py build   /path/to/episode
    .venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py premiere /path/to/episode
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from episode.ingest import ingest  # noqa: E402
from episode.align import load_whisper_words, align_sentences  # noqa: E402
from episode.timeline import build_timeline  # noqa: E402
from episode.review import write_review  # noqa: E402
from episode import premiere  # noqa: E402

WHISPER_MODEL = Path.home() / ".cache" / "whisper" / "ggml-large-v3-turbo.bin"
AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aif", ".aiff", ".flac")


def _one(folder: Path, exts, what: str) -> Path:
    found = sorted(p for p in folder.iterdir() if p.suffix.lower() in exts and not p.name.startswith("."))
    if len(found) != 1:
        sys.exit(f"Expected exactly one {what} in {folder}, found {len(found)}: {[p.name for p in found]}")
    return found[0]


def probe_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def master_wav(vo: Path, build: Path) -> Path:
    """
    One decoded master for everything. Compressed VO (mp3) is decoded differently by ffmpeg and
    Premiere — on episode 001 the lengths differed by ~3 s — so whisper and the timeline both use this WAV.
    """
    wav = build / "vo_master_48k.wav"
    if not (wav.exists() and wav.stat().st_mtime > vo.stat().st_mtime):
        print("[vo] decoding master WAV 48 kHz / 24-bit")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(vo), "-ar", "48000",
                        "-c:a", "pcm_s24le", str(wav)], check=True)
    return wav


def transcribe(vo: Path, build: Path) -> Path:
    words = build / "words.json"
    if words.exists() and words.stat().st_mtime > vo.stat().st_mtime:
        print(f"[transcribe] reuse {words.name}")
        return words
    wav = build / "vo_16k.wav"
    print("[transcribe] converting to 16 kHz mono")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(vo), "-ar", "16000", "-ac", "1", str(wav)], check=True)
    print("[transcribe] whisper large-v3-turbo (≈5 min per hour of audio on Apple Silicon)")
    subprocess.run(["whisper-cli", "-m", str(WHISPER_MODEL), "-f", str(wav), "-l", "en",
                    "-ml", "1", "-sow", "-oj", "-of", str(build / "words"), "-np"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wav.unlink(missing_ok=True)
    return words


def cmd_build(episode: Path) -> None:
    material, build = episode / "material", episode / "build"
    build.mkdir(exist_ok=True)
    docx = _one(material, (".docx",), "script .docx")
    vo = master_wav(_one(material, AUDIO_EXTS, "voice over file"), build)

    script = ingest(docx)
    (build / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    sentences = [dict(b) for b in script["blocks"] if b["kind"] == "narration"]
    print(f"[ingest] {len(script['sections'])} sections · {len(sentences)} sentences · "
          f"{sum(1 for b in script['blocks'] if b['kind'] == 'cue')} client cues")

    words = load_whisper_words(transcribe(vo, build))
    report = align_sentences(sentences, words)
    print(f"[align] {report['well_matched']}/{report['sentences']} sentences matched · "
          f"token coverage {report['token_coverage']:.0%}")

    timeline = build_timeline(script, sentences, {"file": str(vo), "duration": probe_duration(vo)}, report)
    (build / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")
    write_review(timeline, build / "marking.md")

    st = timeline["stats"]
    print(f"[timeline] {len(timeline['slots'])} slots · {st['gfx_count_client']} client GFX "
          f"({st['gfx_share_client']:.0%} of runtime) · with suggestions {st['gfx_count_with_suggestions']} "
          f"({st['gfx_share_with_suggestions']:.0%})")
    print(f"[out] {build / 'timeline.json'}\n[out] {build / 'marking.md'}")


def cmd_premiere(episode: Path, dry_run: bool) -> None:
    timeline = json.loads((episode / "build" / "timeline.json").read_text(encoding="utf-8"))
    jsx = premiere.assembly_jsx(timeline, episode)
    out = episode / "build" / "premiere_assembly.jsx"
    out.write_text(jsx, encoding="utf-8")
    print(f"[premiere] wrote {out}")
    if dry_run:
        return
    print(premiere.run(out))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="ingest script, transcribe VO, align, write timeline.json + marking.md")
    b.add_argument("episode", type=Path)
    p = sub.add_parser("premiere", help="create sequence, place VO and markers in the open Premiere project")
    p.add_argument("episode", type=Path)
    p.add_argument("--dry-run", action="store_true", help="only write the .jsx, don't send it")
    args = ap.parse_args()
    if args.cmd == "build":
        cmd_build(args.episode.resolve())
    else:
        cmd_premiere(args.episode.resolve(), args.dry_run)


if __name__ == "__main__":
    main()
