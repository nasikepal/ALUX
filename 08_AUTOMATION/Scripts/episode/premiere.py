"""
timeline.json -> ExtendScript for Premiere Pro, sent through the Claude Bridge CEP panel
(`com.feugee.claudebridge`, source in 08_AUTOMATION/premiere-bridge/: it polls
<home>/Library/Application Support/ClaudeBridge/inbox for .jsx files — same path on macOS and Windows —
evals them in Premiere and writes the result to outbox/).

Assembly step 1 (this file): sequence 3840x2160 @ 24 fps, VO on A1, markers for chapters and graphics.
Re-running is safe: the sequence is reused, its markers are cleared and rebuilt, the VO is not re-imported.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

BRIDGE = Path.home() / "Library" / "Application Support" / "ClaudeBridge"
TICKS_PER_SEC = 254016000000

# Premiere marker colour indices
COLOR = {"chapter": 1, "client": 3, "suggested": 4,     # red, orange, yellow
         "full": 3, "overlay": 7, "hold": 1}               # orange (V3), cyan (V4), red

JSX_TEMPLATE = r"""
var DATA = __DATA__;

function findItem(bin, name) {
    for (var i = 0; i < bin.children.numItems; i++) {
        var it = bin.children[i];
        if (it.name === name) return it;
    }
    return null;
}
function findSequence(name) {
    for (var i = 0; i < app.project.sequences.numSequences; i++) {
        if (app.project.sequences[i].name === name) return app.project.sequences[i];
    }
    return null;
}

(function () {
    if (!app.project || !app.project.path) return "ERR: no Premiere project open — open or save a project first";
    var root = app.project.rootItem;

    var bin = findItem(root, DATA.bin);
    if (!bin) bin = root.createBin(DATA.bin);

    var vo = findItem(bin, DATA.voName);
    if (!vo) {
        app.project.importFiles([DATA.voPath], true, bin, false);
        vo = findItem(bin, DATA.voName);
        if (!vo) return "ERR: VO import failed: " + DATA.voPath;
    }

    var seq = findSequence(DATA.seqName);
    var created = false;
    if (!seq) {
        seq = app.project.createNewSequenceFromClips(DATA.seqName, [vo], bin);
        if (!seq) return "ERR: could not create sequence";
        created = true;
    }

    var s = seq.getSettings();
    s.videoFrameWidth = DATA.width;
    s.videoFrameHeight = DATA.height;
    var fr = new Time(); fr.ticks = String(DATA.frameTicks);
    s.videoFrameRate = fr;
    seq.setSettings(s);

    // Rebuild markers from timeline.json
    var markers = seq.markers, removed = 0;
    var m = markers.getFirstMarker();
    while (m) { var next = markers.getNextMarker(m); markers.deleteMarker(m); removed++; m = next; }

    var added = 0;
    for (var i = 0; i < DATA.markers.length; i++) {
        var d = DATA.markers[i];
        var mk = markers.createMarker(d.start);
        mk.name = d.name;
        mk.comments = d.comments;
        if (d.end > d.start) mk.end = d.end;  // Premiere takes seconds here, not a Time object
        if (d.chapter) mk.setTypeAsChapter();
        mk.setColorByIndex(d.color);
        added++;
    }

    app.project.activeSequence = seq;
    return "OK sequence=" + seq.name + (created ? " (new)" : " (reused)") +
           " size=" + DATA.width + "x" + DATA.height + " fps=" + DATA.fps +
           " markers_removed=" + removed + " markers_added=" + added;
})();
"""


def _snap(sec: float, fps: int) -> float:
    return round(round(sec * fps) / fps, 6)


def assembly_jsx(tl: Dict[str, Any], episode: Path) -> str:
    fps = tl["fps"]
    markers = []
    for ch in tl["chapters"]:
        markers.append({"start": _snap(ch["start"], fps), "end": 0, "name": ch["title"],
                        "comments": "chapter", "chapter": True, "color": COLOR["chapter"]})
    for g in tl["graphics"]:
        color = COLOR["client"] if g["origin"] == "client" else COLOR["suggested"]
        tag = "" if g["status"] == "approved" else " (SARAN)"
        comments = [f"template: {g['template']}", f"status: {g['status']}", f"isi: {g['label']}"]
        if g.get("file"):
            comments.append(f"file: {g['file']}")
        if g.get("source"):
            comments.append(f"source: {g['source']}")
        markers.append({"start": _snap(g["start"], fps), "end": _snap(g["end"], fps),
                        "name": f"{g['id']} {g['template'].upper()}{tag}", "comments": "\n".join(comments),
                        "chapter": False, "color": color})

    vo_path = Path(tl["vo"]["file"])
    data = {
        "bin": f"ALUX {episode.name}",
        "seqName": f"ALUX {episode.name} — ASSEMBLY",
        "voPath": str(vo_path),
        "voName": vo_path.name,
        "width": tl["resolution"][0],
        "height": tl["resolution"][1],
        "fps": fps,
        "frameTicks": TICKS_PER_SEC // fps,
        "markers": markers,
    }
    # ensure_ascii keeps the payload plain ASCII for ExtendScript's parser
    return JSX_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=True))


def cues_jsx(cues: List[Dict[str, Any]], tl: Dict[str, Any], episode: Path) -> str:
    """Markers from graphics_cues.json: same IDs as the Figma Graphics Map and the asset files, frame-accurate."""
    fps = tl["fps"]
    markers = []
    for ch in tl["chapters"]:
        markers.append({"start": _snap(ch["start"], fps), "end": 0, "name": ch["title"], "comments": "section",
                        "chapter": True, "color": COLOR["chapter"]})
    for c in cues:
        name = f"{c['id']} {c['kind'].upper()}" + (" · HOLD" if c["status"] == "HOLD" else "")
        comments = [f"track: {c['track']} ({'V3 full-frame' if c['track'] == 'FULL' else 'V4 over footage'})",
                    f"in {c['tc_in']}  out {c['tc_out']}  dur {c['duration']}s ({c['frames']}f)",
                    f"asset: {c['asset'] or '-'}", f"isi: {c['content']}"]
        if c["key"]:
            comments.append(f"masuk pada kata: {c['key']}")
        if c["source"]:
            comments.append(f"source: {c['source']}")
        color = COLOR["hold"] if c["status"] == "HOLD" else (COLOR["full"] if c["track"] == "FULL" else COLOR["overlay"])
        markers.append({"start": c["frame_in"] / fps, "end": c["frame_out"] / fps, "name": name,
                        "comments": "\n".join(comments), "chapter": False, "color": color})
    vo_path = Path(tl["vo"]["file"])
    data = {"bin": f"ALUX {episode.name}", "seqName": f"ALUX {episode.name} — ASSEMBLY", "voPath": str(vo_path),
            "voName": vo_path.name, "width": tl["resolution"][0], "height": tl["resolution"][1], "fps": fps,
            "frameTicks": TICKS_PER_SEC // fps, "markers": markers}
    return JSX_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=True))


CAPTIONS_JSX = r"""
var SRT = __SRT__, BIN = __BIN__, SEQ = __SEQ__;
(function () {
    if (!app.project || !app.project.path) return "ERR: no project open";
    var seq = null;
    for (var i = 0; i < app.project.sequences.numSequences; i++) if (app.project.sequences[i].name === SEQ) seq = app.project.sequences[i];
    if (!seq) return "ERR: sequence not found: " + SEQ;
    var root = app.project.rootItem, bin = null;
    for (var j = 0; j < root.children.numItems; j++) if (root.children[j].name === BIN) bin = root.children[j];
    if (!bin) bin = root.createBin(BIN);
    var name = SRT.split("/").pop(), item = null;
    for (var k = 0; k < bin.children.numItems; k++) if (bin.children[k].name === name) item = bin.children[k];
    if (!item) {
        app.project.importFiles([SRT], true, bin, false);
        for (var m = 0; m < bin.children.numItems; m++) if (bin.children[m].name === name) item = bin.children[m];
    }
    if (!item) return "ERR: SRT import failed";
    var before = seq.captionTracks ? seq.captionTracks.numTracks : -1;
    var ok = seq.createCaptionTrack(item, 0, Sequence.CAPTION_FORMAT_SUBTITLE);
    app.project.save();
    return "OK caption track created=" + ok + " item=" + item.name + " captionTracks " + before + "->" + (seq.captionTracks ? seq.captionTracks.numTracks : "?");
})();
"""


def captions_jsx(srt: Path, episode: Path) -> str:
    return (CAPTIONS_JSX.replace("__SRT__", json.dumps(str(srt))).replace("__BIN__", json.dumps(f"ALUX {episode.name}"))
            .replace("__SEQ__", json.dumps(f"ALUX {episode.name} — ASSEMBLY")))


def bridge_alive(max_age_sec: float = 5.0) -> bool:
    hb = BRIDGE / "heartbeat"
    try:
        return (time.time() * 1000 - int(hb.read_text().strip())) < max_age_sec * 1000
    except (OSError, ValueError):
        return False


def run(jsx_path: Path, timeout: int = 180) -> str:
    """Drop the .jsx in the bridge inbox and wait for the panel's answer in outbox (same protocol as bridge/ppro.sh)."""
    if not bridge_alive():
        return ("ERR: Claude Bridge tidak aktif — buka Premiere, lalu Window > Extensions > Claude Bridge. "
                f"JSX tetap tersimpan di {jsx_path}")
    job = f"cmd_{int(time.time() * 1000)}_{os.getpid()}"
    inbox, outbox = BRIDGE / "inbox", BRIDGE / "outbox"
    tmp = inbox / f".{job}.tmp"
    tmp.write_text(Path(jsx_path).read_text(encoding="utf-8"), encoding="utf-8")
    tmp.rename(inbox / f"{job}.jsx")                  # atomic: the panel never reads a half-written file
    answer = outbox / f"{job}.txt"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if answer.exists():
            text = answer.read_text(encoding="utf-8")
            answer.unlink(missing_ok=True)
            return text.strip()
        time.sleep(0.1)
    (inbox / f"{job}.jsx").unlink(missing_ok=True)
    return "TIMEOUT: bridge tidak merespon (panel Claude Bridge tertutup, atau ada dialog terbuka di Premiere)"
