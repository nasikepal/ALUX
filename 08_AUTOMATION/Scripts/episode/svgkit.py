"""
ALUX SVG kit — brand-consistent, animation-ready vector graphics.

Every drawable goes into a named <g id="..."> group. Illustrator turns those groups into layers,
so each group can be animated on its own in After Effects (Illustrator -> AE, "Create Shapes from
Vector Layer") or in Figma. Colors and type follow 00_SYSTEM/brand/alux_tokens.json; text stays
live (font Gilroy) so numbers can be corrected without redrawing.
"""

import html
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

C = {
    "navy950": "#020814", "navy900": "#0A1420", "navy800": "#111F2F", "navy700": "#1D274C",
    "cyan": "#00ADF1", "blue": "#1FA2F0", "blue700": "#1774B0",
    "ice": "#EEF4FB", "mist": "#B6C6D5", "slate": "#5F7488",
    "gold": "#E2A52C", "red": "#EF5350", "green": "#8ED239",
}
W_HEAVY, W_BOLD, W_MEDIUM, W_REGULAR = 900, 700, 500, 400


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


class Svg:
    def __init__(self, w: int, h: int, bg: Optional[str] = "navy900", title: str = ""):
        self.w, self.h, self.parts, self.stack = w, h, [], []
        self.title = title
        if bg:
            self.group("L00_background")
            self.rect(0, 0, w, h, fill=C[bg])
            self.end()

    # --- structure -------------------------------------------------------------------------
    def group(self, gid: str, transform: str = "", opacity: Optional[float] = None) -> "Svg":
        attrs = f' id="{esc(gid)}"'
        if transform:
            attrs += f' transform="{transform}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        self.parts.append(f"<g{attrs}>")
        self.stack.append(gid)
        return self

    def end(self) -> "Svg":
        self.stack.pop()
        self.parts.append("</g>")
        return self

    def raw(self, s: str) -> "Svg":
        self.parts.append(s)
        return self

    # --- primitives ------------------------------------------------------------------------
    def rect(self, x, y, w, h, fill="none", r=0, stroke=None, sw=0, opacity=None, dash=None, id=None):
        a = f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"'
        if r:
            a += f' rx="{r}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if id:
            a += f' id="{esc(id)}"'
        self.parts.append(f"<rect {a}/>")
        return self

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0, opacity=None, id=None, dash=None):
        a = f'cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if id:
            a += f' id="{esc(id)}"'
        self.parts.append(f"<circle {a}/>")
        return self

    def line(self, x1, y1, x2, y2, stroke, sw=8, cap="round", dash=None, opacity=None, id=None):
        a = f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if id:
            a += f' id="{esc(id)}"'
        self.parts.append(f"<line {a}/>")
        return self

    def path(self, d, fill="none", stroke=None, sw=0, cap="round", join="round", opacity=None, id=None, dash=None):
        a = f'd="{d}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" stroke-linejoin="{join}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if id:
            a += f' id="{esc(id)}"'
        self.parts.append(f"<path {a}/>")
        return self

    def text(self, x, y, s, size=56, weight=W_BOLD, fill=None, anchor="start", ls=0.0, upper=False, id=None, opacity=None):
        s = s.upper() if upper else s
        a = (f'x="{x:.1f}" y="{y:.1f}" font-family="Gilroy" font-weight="{weight}" font-size="{size}" '
             f'fill="{fill or C["ice"]}" text-anchor="{anchor}"')
        if ls:
            a += f' letter-spacing="{ls * size:.1f}"'
        if id:
            a += f' id="{esc(id)}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.parts.append(f"<text {a}>{esc(s)}</text>")
        return self

    # --- ALUX vocabulary ---------------------------------------------------------------------
    def eyebrow(self, x, y, s, size=36, fill=None, anchor="start"):
        return self.text(x, y, s, size=size, weight=W_BOLD, fill=fill or C["gold"], ls=0.14, upper=True, anchor=anchor)

    def underline(self, x, y, w=320, h=20, fill=None):
        return self.rect(x, y, w, h, fill=fill or C["cyan"])

    def person(self, cx, cy, s=1.0, fill=None, id=None):
        """Simple person glyph centred on (cx, cy); s=1 -> 60 px tall."""
        f = fill or C["slate"]
        if id:
            self.group(id)
        self.circle(cx, cy - 18 * s, 10 * s, fill=f)
        r = 17 * s
        # shoulders: a half-round body under the head
        self.path(f"M{cx - r:.1f},{cy + 30 * s:.1f} V{cy + 14 * s:.1f} A{r:.1f},{r:.1f} 0 0 1 {cx + r:.1f},{cy + 14 * s:.1f} "
                  f"V{cy + 30 * s:.1f} Z", fill=f)
        if id:
            self.end()
        return self

    def arrow(self, x1, y1, x2, y2, stroke=None, sw=10, head=28, id=None, dash=None):
        stroke = stroke or C["cyan"]
        if id:
            self.group(id)
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * 0.8 * math.cos(ang), y2 - head * 0.8 * math.sin(ang)
        self.line(x1, y1, bx, by, stroke, sw, dash=dash)
        p1 = (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
        p2 = (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
        self.path(f"M{p1[0]:.1f},{p1[1]:.1f} L{x2:.1f},{y2:.1f} L{p2[0]:.1f},{p2[1]:.1f}", stroke=stroke, sw=sw)
        if id:
            self.end()
        return self

    def card(self, x, y, w, h, fill=None, stroke=None, r=32):
        return self.rect(x, y, w, h, fill=fill or C["navy800"], r=r, stroke=stroke, sw=4 if stroke else 0)

    def coin(self, cx, cy, r=26, fill=None):
        f = fill or C["gold"]
        self.circle(cx, cy, r, fill=f)
        self.circle(cx, cy, r * 0.62, fill="none", stroke=C["navy900"], sw=max(2, r * 0.12), opacity=0.35)
        return self

    def source(self, s, x=None, y=None):
        x = 80 if x is None else x
        y = self.h - 60 if y is None else y
        self.group("L99_source")
        self.rect(x, y - 30, 8, 36, fill=C["cyan"])
        self.text(x + 28, y, s, size=30, weight=W_MEDIUM, fill=C["mist"], ls=0.02, upper=True)
        return self.end()

    # --- output ------------------------------------------------------------------------------
    def svg(self) -> str:
        assert not self.stack, f"unclosed groups: {self.stack}"
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">')
        title = f"<title>{esc(self.title)}</title>" if self.title else ""
        return head + title + "".join(self.parts) + "</svg>"

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.svg(), encoding="utf-8")
        return path


def person_grid(svg: Svg, x0, y0, cols, rows, gap, highlight: Sequence[int], hi_color, base_color=None, s=1.0,
                gid="L10_people", hi_gid="L11_people_highlight"):
    """cols x rows people; indices in `highlight` go into their own group so they can be animated apart."""
    base_color = base_color or C["slate"]
    hl = set(highlight)
    svg.group(gid)
    for i in range(cols * rows):
        if i in hl:
            continue
        c, r = i % cols, i // cols
        svg.person(x0 + c * gap, y0 + r * gap, s, fill=base_color, id=f"p{i + 1:03d}")
    svg.end()
    svg.group(hi_gid)
    for i in sorted(hl):
        c, r = i % cols, i // cols
        svg.person(x0 + c * gap, y0 + r * gap, s, fill=hi_color, id=f"p{i + 1:03d}")
    svg.end()


def render_preview(svg_path: Path, png_path: Path, width: int = 1280) -> Optional[Path]:
    """PNG preview through macOS Quick Look (WebKit, sees locally installed Gilroy)."""
    if not shutil.which("qlmanage"):
        return None
    txt = svg_path.read_text(encoding="utf-8")
    w, h = _wh(txt)
    scale = width / w / 2.0  # Quick Look draws at 2x
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_svg = tmp_dir / "p.svg"
    tmp_svg.write_text(txt.replace(f'width="{int(w)}" height="{int(h)}"', f'width="{w * scale:.0f}" height="{h * scale:.0f}"', 1),
                       encoding="utf-8")
    side = int(max(w, h) * scale * 2) + 2
    subprocess.run(["qlmanage", "-t", "-s", str(side), "-o", str(tmp_dir), str(tmp_svg)], capture_output=True)
    out = tmp_dir / "p.svg.png"
    if not out.exists():
        return None
    subprocess.run(["magick", str(out), "-crop", f"{width}x{int(h / w * width)}+0+0", "+repage", str(png_path)], check=True)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return png_path


def _wh(txt: str) -> Tuple[float, float]:
    vb = txt.split('viewBox="', 1)[1].split('"', 1)[0].split()
    return float(vb[2]), float(vb[3])


def contact_sheet(pngs: List[Path], out: Path, cols: int = 4, tile: int = 640):
    """Grid of previews with file names, for one-glance review."""
    args = ["magick", "montage", "-label", "%t", "-font", str(Path.home() / "Library/Fonts/Gilroy-Medium.ttf"),
            "-pointsize", "16"] + [str(p) for p in pngs] + [
        "-geometry", f"{tile}x{int(tile * 9 / 16)}+12+12", "-tile", f"{cols}x", "-background", "#E9E7E2", str(out)]
    subprocess.run(args, check=True)
    return out
