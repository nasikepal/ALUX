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
from episode.timeline import build_timeline, tc  # noqa: E402
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


def transcribe_chunked(wav16: Path, out_json: Path, target: float = 25.0) -> Path:
    """
    Whisper on the whole file skips sentences after long pauses (EP001 lost four read-aloud chapter titles)
    and its word times drift there by up to 3.5 s. Transcribing ~25 s chunks cut at silences, with DTW
    token timing (needs flash attention off), fixes both. Output: whisper-style JSON with absolute times.
    """
    import tempfile
    from episode.captions import Speech
    sp = Speech(wav16)
    total = len(sp.frames) / 100.0
    cuts, t = [0.0], 0.0
    while t + target < total:
        # quietest 10 ms frame within +-4 s of the target cut point
        a, b = int((t + target - 4) * 100), int((t + target + 4) * 100)
        q = min(range(a, min(b, len(sp.frames))), key=lambda i: sp.frames[i])
        t = q / 100.0
        cuts.append(t)
    cuts.append(total)
    tmp = Path(tempfile.mkdtemp())
    merged = []
    for k, (c0, c1) in enumerate(zip(cuts, cuts[1:])):
        clip = tmp / f"c{k:04d}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{c0:.2f}", "-t", f"{c1 - c0:.2f}", "-i", str(wav16),
                        str(clip)], check=True)
        subprocess.run(["whisper-cli", "-m", str(WHISPER_MODEL), "-f", str(clip), "-l", "en", "-ml", "1", "-sow", "-ojf",
                        "-dtw", "large.v3.turbo", "-nfa", "-of", str(clip.with_suffix("")), "-np"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        data = json.loads(clip.with_suffix(".json").read_text(encoding="utf-8"))
        for seg in data.get("transcription", []):
            toks = [x for x in seg.get("tokens", []) if not x.get("text", "").startswith("[") and x.get("t_dtw", -1) != -1]
            o = seg["offsets"]
            start = (min(x["t_dtw"] for x in toks) / 100.0) if toks else o["from"] / 1000.0
            end = max(o["to"] / 1000.0, start)
            ms = lambda v: int(round((v + c0) * 1000))
            merged.append({"text": seg["text"], "offsets": {"from": ms(start), "to": ms(end)}})
        print(f"\r[transcribe] chunk {k + 1}/{len(cuts) - 1}", end="", flush=True)
    print()
    out_json.write_text(json.dumps({"transcription": merged, "method": "chunked+dtw"}, ensure_ascii=False), encoding="utf-8")
    return out_json


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


def asset_index(episode: Path, gmap, fill) -> dict:
    """map_id -> file the editor places: generated artwork, or the MOGRT the template will become."""
    root = episode / "assets" / "graphics"
    out = {}
    for it in gmap:
        e = fill.get(it["map_id"]) or {}
        art = e.get("art")
        hit = next(root.glob(f"*/{art}.svg"), None) if art else None
        if hit:
            out[it["map_id"]] = str(hit.relative_to(episode))
        elif e.get("template"):
            out[it["map_id"]] = f"MOGRT ALUX_{e['template']}.mogrt (belum dibuat)"
    return out


def cmd_retime(episode: Path, words_file: str) -> None:
    """Re-align the timeline's sentences to a better transcript; graphics definitions and IDs stay untouched."""
    build = episode / "build"
    tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    sentences = [{"id": s["sentence"], "text": s["text"], "section": s["section"]} for s in tl["slots"]]
    report = align_sentences(sentences, load_whisper_words(build / words_file))
    for slot, sen in zip(tl["slots"], sentences):
        slot.update(start=sen["start"], end=sen["slot_end"], match=sen["match"], interpolated=sen.get("interpolated", False))
        slot["tc_in"], slot["tc_out"] = tc(sen["start"]), tc(sen["slot_end"])
    first = {}
    for sl in tl["slots"]:
        first.setdefault(sl["section"], sl["start"])
    for ch in tl["chapters"]:
        ch["start"] = first.get(ch["id"], ch["start"])
    tl["alignment"] = report
    tl["words_file"] = words_file
    (build / "timeline.json").write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[retime] {report['well_matched']}/{report['sentences']} sentences matched · coverage {report['token_coverage']:.0%}")


def cmd_cues(episode: Path, words_file: str) -> None:
    from episode.cues import build_cues, load_words, write_outputs
    build = episode / "build"
    tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    gmap = json.loads((build / "graphics_map.json").read_text(encoding="utf-8"))
    fill = json.loads((build / "graphics_fill.json").read_text(encoding="utf-8"))
    words = load_words(build / words_file)
    keys_file = build / "cue_keys.json"
    phrases = json.loads(keys_file.read_text(encoding="utf-8")) if keys_file.exists() else {}
    cues, log = build_cues(tl, gmap, fill, words, asset_index(episode, gmap, fill), phrases)
    j, c = write_outputs(cues, log, build)
    keyed = sum(1 for x in cues if x["key"])
    print(f"[cues] {len(cues)} cues · {keyed} keyed to a spoken word · {len(log)} adjustments")
    print(f"[out] {j}\n[out] {c}")


def cmd_captions(episode: Path, words_file: str, check_file: str, to_premiere: bool) -> None:
    from episode.captions import script_words, merge, segment, time_captions, write_srt, qc, srt_time
    from episode.cues import load_words
    build = episode / "build"
    vo = load_words(build / words_file)
    check = load_words(build / check_file) if check_file and (build / check_file).exists() else None
    script = json.loads((build / "script.json").read_text(encoding="utf-8"))
    from episode.captions import Speech
    wav16 = build / "vo_16k_mono.wav"
    if not wav16.exists():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(build / "vo_master_48k.wav"), "-ar", "16000",
                        "-ac", "1", "-c:a", "pcm_s16le", str(wav16)], check=True)
    from episode.captions import relisten
    models = [(WHISPER_MODEL, []), (WHISPER_MODEL, ["-bs", "5", "-bo", "5"])]
    base = Path.home() / ".cache" / "whisper" / "ggml-base.en.bin"
    if base.exists():
        models.append((base, []))
    tiebreak = lambda t0, t1, cands: relisten(wav16, t0, t1, cands, models)
    words, log = merge(vo, script_words(script), check, Speech(wav16), tiebreak)
    caps = time_captions(segment(words))
    title = script["title"].split(":")[-1].strip().title().replace(" ", "_")
    srt = write_srt(caps, build / f"{episode.name}_{title}_captions.srt")
    report = qc(caps)
    review = [l for l in log if l["kind"] == "REVIEW"]
    lines = ["---", "type: caption_review", f"captions: {report['captions']}", f"review_items: {len(review)}", "---", "",
             "# Caption review", "", "Listen to each line below and fix the SRT if the VO says something else.", "",
             "| TC | Why | VO transcript | Script | 2nd pass |", "|---|---|---|---|---|"]
    for l in review:
        tcx = srt_time(round(l["t"] * 24))[:8]
        lines.append(f"| `{tcx}` | {l.get('why', '')} | {l['vo']} | {l['script']} | {l.get('pass2', '')} |")
    from collections import Counter
    decided = [l for l in log if l["kind"] == "decided by re-listening the clip"]
    if decided:
        lines += ["", "## Decided by re-listening the clip (majority of 3 transcriptions)", "",
                  "| TC | VO (1st pass) | Script | Chosen | Heard |", "|---|---|---|---|---|"]
        for l in decided:
            lines.append(f"| `{srt_time(round(l['t'] * 24))[:8]}` | {l['vo']} | {l['script']} | **{l['chosen']}** | {l['evidence'][:120]} |")
    lines += ["", "## Automatic decisions", ""] + [f"- {k}: {v}" for k, v in Counter(l["kind"] for l in log).items()]
    lines += ["", "## QC", ""] + [f"- {k}: {v}" for k, v in report.items()]
    (build / "captions_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (build / "captions_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[captions] {report['captions']} captions · review {len(review)} · QC {report}")
    print(f"[out] {srt}\n[out] {build / 'captions_review.md'}")
    if to_premiere:
        jsx = build / "premiere_captions.jsx"
        jsx.write_text(premiere.captions_jsx(srt, episode), encoding="utf-8")
        print(premiere.run(jsx))


def cmd_premiere(episode: Path, dry_run: bool) -> None:
    timeline = json.loads((episode / "build" / "timeline.json").read_text(encoding="utf-8"))
    cues_file = episode / "build" / "graphics_cues.json"
    if cues_file.exists():
        jsx = premiere.cues_jsx(json.loads(cues_file.read_text(encoding="utf-8"))["cues"], timeline, episode)
    else:
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
    tc_ = sub.add_parser("transcribe", help="chunked + DTW transcription (accurate word times, no skipped lines)")
    tc_.add_argument("episode", type=Path)
    tc_.add_argument("--out", default="words_chunked.json")
    rt = sub.add_parser("retime", help="re-align timeline sentences to a better transcript (keeps graphic IDs)")
    rt.add_argument("episode", type=Path)
    rt.add_argument("--words", default="words_final.json")
    q = sub.add_parser("cues", help="lock every graphic to its spoken word -> graphics_cues.json/.csv")
    q.add_argument("episode", type=Path)
    q.add_argument("--words", default="words.json", help="whisper JSON in build/ (use words_dtw.json for DTW timing)")
    cp = sub.add_parser("captions", help="VO + script -> timed SRT, review list, optional Premiere caption track")
    cp.add_argument("episode", type=Path)
    cp.add_argument("--words", default="words.json")
    cp.add_argument("--check", default="words_pass2.json", help="independent 2nd transcription used as tie-breaker")
    cp.add_argument("--premiere", action="store_true", help="import the SRT as a caption track")
    p = sub.add_parser("premiere", help="create sequence, place VO and markers in the open Premiere project")
    p.add_argument("episode", type=Path)
    p.add_argument("--dry-run", action="store_true", help="only write the .jsx, don't send it")
    args = ap.parse_args()
    if args.cmd == "build":
        cmd_build(args.episode.resolve())
    elif args.cmd == "transcribe":
        ep = args.episode.resolve()
        print(transcribe_chunked(ep / "build" / "vo_16k_mono.wav", ep / "build" / args.out))
    elif args.cmd == "captions":
        cmd_captions(args.episode.resolve(), args.words, args.check, args.premiere)
    elif args.cmd == "retime":
        cmd_retime(args.episode.resolve(), args.words)
    elif args.cmd == "cues":
        cmd_cues(args.episode.resolve(), args.words)
    else:
        cmd_premiere(args.episode.resolve(), args.dry_run)


if __name__ == "__main__":
    main()
