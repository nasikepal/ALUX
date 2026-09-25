"""
graphics_map.json (+ an episode fill file) -> a Figma plugin that fills the episode's Graphics Map
with real ALUX template instances.

Why a plugin: the Figma MCP runs on Figma's servers and cannot edit text set in Gilroy (a local font).
The generated plugin runs in Figma Desktop, where Gilroy is installed.

The fill file (build/graphics_fill.json) maps a graphic id to template fields. It is written by a
human or by Claude from the script — values must come from the script/sources, never invented.
Graphics with no template yet are labelled on their card instead of being faked.
"""

import json
from pathlib import Path
from typing import Any, Dict

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "figma-plugins" / "alux-fill-map"
TEMPLATE_JS = PLUGIN_DIR / "code.template.js"


def build_plugin(graphics_map: Path, fill: Path, episode_label: str, art_dir: Path = None) -> Path:
    """art_dir: folder with stills/, illustrations/, explainer/ SVGs; fill entries reference them by "art": <stem>."""
    items = json.loads(graphics_map.read_text(encoding="utf-8"))
    spec: Dict[str, Any] = json.loads(fill.read_text(encoding="utf-8"))
    art: Dict[str, str] = {}
    if art_dir and art_dir.exists():
        for svg in art_dir.glob("*/*.svg"):
            art[svg.stem] = svg.read_text(encoding="utf-8")
    missing = sorted({e["art"] for e in spec.values() if isinstance(e, dict) and e.get("art")} - set(art))
    if missing:
        raise SystemExit(f"art referenced but not found: {missing}")
    cards = []
    for it in items:
        entry = spec.get(it["map_id"])
        cards.append({
            "id": it["map_id"],
            "type": it["type"],
            "fill": entry,  # None -> no template yet
        })
    used = {e["art"] for e in spec.values() if isinstance(e, dict) and e.get("art")}
    payload = {"episode": episode_label, "cards": cards, "art": {k: v for k, v in art.items() if k in used}}
    code = TEMPLATE_JS.read_text(encoding="utf-8").replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    out = PLUGIN_DIR / "code.js"
    out.write_text(code, encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    ep = Path(sys.argv[1])
    print(build_plugin(ep / "build" / "graphics_map.json", ep / "build" / "graphics_fill.json", ep.name,
                       ep / "assets" / "graphics"))
