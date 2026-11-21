#!/usr/bin/env python3
"""Generate SVG replacements for suitable responsive raster assets."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import vtracer
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

ROOT = Path(__file__).resolve().parents[1]
RESP = ROOT / "responsive" / "image"
FONT_BOLD = Path("/tmp/fonts/NotoSansKR-Bold.otf")
FONT_MED = Path("/tmp/fonts/NotoSansKR-Medium.otf")
FONT_LATIN = Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf")
TMP = Path("/tmp/svg-build")
TMP.mkdir(parents=True, exist_ok=True)

CONVERTED: list[tuple[str, str]] = []


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    CONVERTED.append((rel, "hand" if "vtracer" not in content.lower() else "trace"))


def _pick_font(text: str, font_path: Path) -> Path:
    """Use Latin Noto Sans for ASCII; keep KR font for Hangul."""
    if all(ord(ch) < 128 for ch in text):
        return FONT_LATIN if FONT_LATIN.exists() else font_path
    return font_path


def text_paths(
    text: str,
    font_path: Path,
    font_size: float,
    x: float,
    y: float,
    fill: str,
    *,
    anchor: str = "start",
    letter_spacing: float = 0.0,
) -> str:
    font_path = _pick_font(text, font_path)
    font = TTFont(str(font_path))
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    scale = font_size / upem
    hmtx = font["hmtx"].metrics

    advances = []
    for ch in text:
        name = cmap.get(ord(ch))
        if not name:
            advances.append(font_size * 0.5)
            continue
        advances.append(hmtx[name][0] * scale + letter_spacing)
    total = sum(advances) - (letter_spacing if text else 0)
    if anchor == "middle":
        cursor = x - total / 2
    elif anchor == "end":
        cursor = x - total
    else:
        cursor = x

    parts = []
    for ch, adv in zip(text, advances):
        name = cmap.get(ord(ch))
        if not name:
            cursor += adv
            continue
        pen = SVGPathPen(glyph_set)
        # SVG y grows down; font y grows up
        tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, cursor, y))
        glyph_set[name].draw(tpen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path fill="{fill}" d="{d}"/>')
        cursor += adv
    return "\n  ".join(parts)


def cheongna_mark(cx: float, cy: float, r_outer: float, r_inner: float, fill: str, rot: float = -25) -> str:
    """Tilted ring/C mark approximating brand CI."""
    # Draw as ellipse ring via two circles with evenodd, then rotate
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path fill="{fill}" fill-rule="evenodd" '
        f'd="M0,{-r_outer} A{r_outer},{r_outer * 0.82} 0 1 1 0,{r_outer} '
        f'A{r_outer},{r_outer * 0.82} 0 1 1 0,{-r_outer} Z '
        f'M0,{-r_inner} A{r_inner},{r_inner * 0.82} 0 1 0 0,{r_inner} '
        f'A{r_inner},{r_inner * 0.82} 0 1 0 0,{-r_inner} Z"/></g>'
    )


def build_header_logo() -> None:
    # 186x39 matching original
    mark = cheongna_mark(18, 14, 13, 7.2, "url(#cGrad)", -28)
    en = text_paths("CHEONGNA ENERGY", FONT_BOLD, 4.2, 18, 32, "#1a1a1a", anchor="middle", letter_spacing=0.4)
    ko = text_paths("청라에너지주식회사", FONT_BOLD, 15, 42, 26, "#0050a0", letter_spacing=0.2)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="186" height="39" viewBox="0 0 186 39" role="img" aria-label="청라에너지주식회사">
  <defs>
    <linearGradient id="cGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#5ec8d8"/>
      <stop offset="55%" stop-color="#1aa8bc"/>
      <stop offset="100%" stop-color="#0a8fa8"/>
    </linearGradient>
  </defs>
  {mark}
  {en}
  {ko}
</svg>
'''
    write(RESP / "main" / "img_h1.svg", svg)


def build_footer_logo() -> None:
    mark = cheongna_mark(14, 10, 9.5, 5.2, "#8a8a8a", -28)
    en = text_paths("CHEONGNA ENERGY", FONT_BOLD, 3.0, 14, 22.5, "#808080", anchor="middle", letter_spacing=0.15)
    ko = text_paths("청라에너지주식회사", FONT_BOLD, 11, 32, 17, "#808080", letter_spacing=0.15)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="145" height="26" viewBox="0 0 145 26" role="img" aria-label="청라에너지주식회사">
  {mark}
  {en}
  {ko}
</svg>
'''
    write(RESP / "main" / "img_footer_logo.svg", svg)


def build_concept_logos() -> None:
    # Vertical CI
    mark = cheongna_mark(114.5, 58, 42, 22, "#00a0b0", -28)
    en1 = text_paths("CHEONGNA", FONT_BOLD, 18, 114.5, 118, "#111", anchor="middle", letter_spacing=1.2)
    en2 = text_paths("ENERGY", FONT_BOLD, 18, 114.5, 140, "#111", anchor="middle", letter_spacing=2.5)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="229" height="158" viewBox="0 0 229 158" role="img" aria-label="CHEONGNA ENERGY">
  {mark}
  {en1}
  {en2}
</svg>
'''
    write(RESP / "pr" / "img_concept_01.svg", svg)

    # Horizontal combination
    mark = cheongna_mark(70, 52, 38, 20, "#0084b1", -28)
    en1 = text_paths("CHEONGNA", FONT_BOLD, 11, 70, 100, "#111", anchor="middle", letter_spacing=0.8)
    en2 = text_paths("ENERGY", FONT_BOLD, 11, 70, 114, "#111", anchor="middle", letter_spacing=1.6)
    ko = text_paths("청라에너지주식회사", FONT_BOLD, 36, 145, 78, "#0084b1", letter_spacing=0.5)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="650" height="145" viewBox="0 0 650 145" role="img" aria-label="청라에너지주식회사">
  {mark}
  {en1}
  {en2}
  {ko}
</svg>
'''
    write(RESP / "pr" / "img_concept_02.svg", svg)


def section_title(filename: str, label: str, icon_svg: str) -> None:
    title = text_paths(label, FONT_BOLD, 22, 78, 58, "#4a4a4a", letter_spacing=0.3)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="195" height="104" viewBox="0 0 195 104" role="img" aria-label="{label}">
  <rect width="195" height="103" fill="#fff"/>
  <g transform="translate(18,28)">{icon_svg}</g>
  {title}
  <line x1="0" y1="103.5" x2="195" y2="103.5" stroke="#d0d0d0" stroke-width="1"/>
</svg>
'''
    write(RESP / "common" / filename, svg)


def build_section_titles() -> None:
    teal = "#58a0b8"
    icons = {
        "img_company_title.svg": (
            "회사소개",
            f'<rect x="0" y="4" width="16" height="36" fill="{teal}"/><rect x="2" y="8" width="4" height="5" fill="#fff"/><rect x="10" y="8" width="4" height="5" fill="#fff"/><rect x="2" y="16" width="4" height="5" fill="#fff"/><rect x="10" y="16" width="4" height="5" fill="#fff"/><rect x="2" y="24" width="4" height="5" fill="#fff"/><rect x="10" y="24" width="4" height="5" fill="#fff"/><path d="M18 18h22v22H18z" fill="{teal}"/><path d="M18 18l22-10v10z" fill="{teal}"/><rect x="22" y="24" width="4" height="5" fill="#fff"/><rect x="30" y="24" width="4" height="5" fill="#fff"/><rect x="22" y="32" width="4" height="5" fill="#fff"/><rect x="30" y="32" width="4" height="5" fill="#fff"/>',
        ),
        "img_business_title.svg": (
            "사업소개",
            f'<circle cx="22" cy="22" r="18" fill="none" stroke="{teal}" stroke-width="4"/><path d="M10 26c6-10 18-10 24 0" fill="none" stroke="{teal}" stroke-width="3"/><rect x="16" y="14" width="5" height="12" fill="{teal}"/><rect x="24" y="10" width="5" height="16" fill="{teal}"/>',
        ),
        "img_pr_title.svg": (
            "홍보센터",
            f'<rect x="8" y="6" width="28" height="32" rx="2" fill="none" stroke="{teal}" stroke-width="3"/><circle cx="22" cy="18" r="6" fill="none" stroke="{teal}" stroke-width="2"/><path d="M14 34c3-6 13-6 16 0" fill="none" stroke="{teal}" stroke-width="2"/>',
        ),
        "img_bidding_title.svg": (
            "입찰안내",
            f'<rect x="10" y="8" width="24" height="30" rx="2" fill="none" stroke="{teal}" stroke-width="3"/><path d="M16 4h12v8H16z" fill="{teal}"/><line x1="16" y1="18" x2="28" y2="18" stroke="{teal}" stroke-width="2"/><line x1="16" y1="24" x2="28" y2="24" stroke="{teal}" stroke-width="2"/><line x1="16" y1="30" x2="24" y2="30" stroke="{teal}" stroke-width="2"/>',
        ),
        "img_info_title.svg": (
            "정보센터",
            f'<rect x="6" y="10" width="32" height="24" rx="2" fill="none" stroke="{teal}" stroke-width="3"/><circle cx="16" cy="22" r="4" fill="{teal}"/><line x1="24" y1="18" x2="34" y2="18" stroke="{teal}" stroke-width="2"/><line x1="24" y1="26" x2="32" y2="26" stroke="{teal}" stroke-width="2"/>',
        ),
        "img_customer_title.svg": (
            "고객서비스",
            f'<circle cx="22" cy="14" r="8" fill="none" stroke="{teal}" stroke-width="3"/><path d="M8 40c2-12 26-12 28 0" fill="none" stroke="{teal}" stroke-width="3"/>',
        ),
        "img_sitemap_title.svg": (
            "사이트맵",
            f'<rect x="14" y="4" width="16" height="12" rx="2" fill="{teal}"/><rect x="4" y="28" width="14" height="12" rx="2" fill="{teal}"/><rect x="26" y="28" width="14" height="12" rx="2" fill="{teal}"/><path d="M22 16v6M11 28v-6h22v6" fill="none" stroke="{teal}" stroke-width="2"/>',
        ),
        "recruitment.svg": (
            "인재채용",
            f'<circle cx="22" cy="12" r="8" fill="none" stroke="{teal}" stroke-width="3"/><path d="M8 40c2-12 26-12 28 0" fill="none" stroke="{teal}" stroke-width="3"/><path d="M20 22l2 10 2-10z" fill="{teal}"/>',
        ),
    }
    for fname, (label, icon) in icons.items():
        section_title(fname, label, icon)


def build_sitemap_labels() -> None:
    labels = [
        ("img_sitemap_t01.svg", "회사소개"),
        ("img_sitemap_t02.svg", "사업소개"),
        ("img_sitemap_t03.svg", "홍보센터"),
        ("img_sitemap_t04.svg", "입찰안내"),
        ("img_sitemap_t05.svg", "정보센터"),
        ("img_sitemap_t06.svg", "고객서비스"),
        ("img_sitemap_t07.svg", "인재채용"),
        ("img_sitemap_t08.svg", "검단컨소시엄"),
    ]
    for fname, label in labels:
        # Measure approx width
        w = 14 + len(label) * 14
        paths = text_paths(label, FONT_BOLD, 14, 0, 14, "#333")
        # Get better width via font
        font = TTFont(str(FONT_BOLD))
        cmap = font.getBestCmap()
        hmtx = font["hmtx"].metrics
        upem = font["head"].unitsPerEm
        scale = 14 / upem
        width = sum(hmtx[cmap[ord(ch)]][0] * scale for ch in label if ord(ch) in cmap) + 4
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="18" viewBox="0 0 {width:.0f} 18" role="img" aria-label="{label}">
  {paths}
</svg>
'''
        write(RESP / "common" / fname, svg)


def _is_near_white_hex(fill: str) -> bool:
    fill = fill.strip().lstrip("#")
    if len(fill) == 3:
        fill = "".join(c * 2 for c in fill)
    if len(fill) != 6 or any(c not in "0123456789abcdefABCDEF" for c in fill):
        return False
    r, g, b = int(fill[0:2], 16), int(fill[2:4], 16), int(fill[4:6], 16)
    return r >= 0xF0 and g >= 0xF0 and b >= 0xF0


def finalize_traced_svg(text: str, *, src_w: int, src_h: int) -> str:
    """Drop opaque full-canvas near-white bg; restore source intrinsic size."""
    # Remove full-canvas near-white rectangle paths (e.g. #FEFEFE / #FFFFFF).
    def drop_bg(match: re.Match[str]) -> str:
        fill = match.group(1)
        return "" if _is_near_white_hex(fill) else match.group(0)

    text = re.sub(
        r'<path d="M0(?:\s|,)0[^"]*" fill="(#[0-9A-Fa-f]{3,8})"[^/]*/>\s*',
        drop_bg,
        text,
        count=3,
    )
    # Restore intrinsic size to the pre-supersample source; keep traced coords in viewBox.
    m = re.search(r'<svg([^>]*)>', text, flags=re.I)
    if m:
        attrs = m.group(1)
        tw = re.search(r'\bwidth="(\d+(?:\.\d+)?)"', attrs)
        th = re.search(r'\bheight="(\d+(?:\.\d+)?)"', attrs)
        traced_w = tw.group(1) if tw else str(src_w)
        traced_h = th.group(1) if th else str(src_h)
        attrs = re.sub(r'\s*\bwidth="[^"]*"', "", attrs)
        attrs = re.sub(r'\s*\bheight="[^"]*"', "", attrs)
        attrs = re.sub(r'\s*\bviewBox="[^"]*"', "", attrs)
        new_open = (
            f'<svg{attrs} width="{src_w}" height="{src_h}" '
            f'viewBox="0 0 {traced_w} {traced_h}">'
        )
        text = text[: m.start()] + new_open + text[m.end() :]
    return text


def strip_bg_and_trace(src: Path, dest: Path, *, scale: int = 3, binary: bool = False, threshold: int = 200) -> None:
    im = Image.open(src)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    src_w, src_h = im.size
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
    # Make near-white transparent for cleaner SVG, then flatten to white for tracer
    datas = []
    for r, g, b, a in im.getdata():
        if a < 40 or (r > 248 and g > 248 and b > 248):
            datas.append((255, 255, 255, 255))
        else:
            datas.append((r, g, b, 255))
    im.putdata(datas)
    png = TMP / f"{src.stem}_trace.png"
    if binary:
        gray = im.convert("L")
        bw = gray.point(lambda p: 255 if p > threshold else 0)
        bw.save(png)
        vtracer.convert_image_to_svg_py(
            str(png),
            str(dest),
            colormode="binary",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=4,
            color_precision=6,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=2,
        )
    else:
        im.convert("RGB").save(png)
        vtracer.convert_image_to_svg_py(
            str(png),
            str(dest),
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=6,
            color_precision=6,
            layer_difference=22,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=2,
        )
    text = finalize_traced_svg(dest.read_text(encoding="utf-8"), src_w=src_w, src_h=src_h)
    dest.write_text(text, encoding="utf-8")
    try:
        rel = dest.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        rel = dest.as_posix()
    CONVERTED.append((rel, "trace"))


def build_traced_assets() -> None:
    # Customer icons
    for p in sorted((RESP / "customer").glob("cus_ico*.png")):
        strip_bg_and_trace(p, p.with_suffix(".svg"), scale=3)

    # Org charts (diagrams)
    for name in ("img_organization.gif", "img_organization_n.gif"):
        src = RESP / "company" / name
        strip_bg_and_trace(src, src.with_suffix(".svg"), scale=2)

    # Infocenter diagram
    src = RESP / "information" / "img_infocenter.gif"
    if src.exists():
        strip_bg_and_trace(src, src.with_suffix(".svg"), scale=2)

    # Small UI / marks via binary trace (skip ico_pdf / ico_han — hand-drawn)
    for rel in [
        "common/ico_just_write.gif",
        "company/img_history_title.gif",
        "company/img_ceo_text.gif",
        "company/img_lsh_sign.gif",
        "company/btn_damu_link.gif",
        "company/bg_icon_01.gif",
        "company/bg_icon_02.gif",
        "company/bg_icon_03.gif",
        "company/bg_group_line.gif",
    ]:
        src = RESP / rel
        if src.exists():
            strip_bg_and_trace(src, src.with_suffix(".svg"), scale=4, binary=True, threshold=190)

    # Partner logos — finer color layers
    for name in ("img_group_01.gif", "img_group_02.gif"):
        src = RESP / "company" / name
        im = Image.open(src).convert("RGBA")
        im = im.resize((im.width * 4, im.height * 4), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        png = TMP / f"{src.stem}_hi.png"
        Image.alpha_composite(bg, im).convert("RGB").save(png)
        dest = src.with_suffix(".svg")
        vtracer.convert_image_to_svg_py(
            str(png),
            str(dest),
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=2,
            color_precision=8,
            layer_difference=10,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=2,
        )
        CONVERTED.append((dest.relative_to(ROOT).as_posix(), "trace"))


def icon_svg(view: int, body: str, stroke: str = "#989898", fill: str = "none") -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{view}" height="{view}" viewBox="0 0 32 32" fill="none" stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  {body}
</svg>
'''


def build_content_icons() -> None:
    g = "#989898"
    blue = "#00a0c0"
    icons = {
        "benefits1.svg": icon_svg(
            32,
            '<path d="M10 6v20M10 10h3l1 4 1-8 1 8 1-4h3M18 8c0 0 2-1 3 1v17"/>',
        ),
        "benefits2.svg": icon_svg(
            34,
            f'<rect x="8" y="12" width="16" height="12" rx="1" fill="{g}" stroke="none"/><rect x="13" y="8" width="6" height="4" fill="none" stroke="{g}" stroke-width="1.6"/><rect x="14.5" y="16" width="3" height="4" fill="#fff" stroke="none"/>',
        ),
        "benefits3.svg": icon_svg(
            34,
            f'<path d="M16 6c2.5 0 4.5 2 4.5 4.2 0 3.5-4.5 7.3-4.5 7.3S11.5 13.7 11.5 10.2C11.5 8 13.5 6 16 6z" fill="none"/><path d="M7 22h4v3H7z"/><path d="M11 25c4 0 10-1 12-5"/>',
        ),
        "benefits4.svg": icon_svg(
            34,
            '<rect x="8" y="14" width="16" height="12"/><line x1="8" y1="18" x2="24" y2="18"/><path d="M16 14v12"/><path d="M16 14c-3-4-6-2-6 0 3 0 6 0 6 0z"/><path d="M16 14c3-4 6-2 6 0-3 0-6 0-6 0z"/><path d="M14 26l2-3 2 3"/>',
        ),
        "benefits5.svg": icon_svg(
            36,
            f'<path d="M6 26V14l10-8 10 8v12z" fill="none"/><rect x="12" y="16" width="3" height="3" fill="{g}" stroke="none"/><rect x="17" y="16" width="3" height="3" fill="{g}" stroke="none"/><rect x="12" y="21" width="3" height="3" fill="{g}" stroke="none"/><rect x="17" y="21" width="3" height="3" fill="{g}" stroke="none"/>',
        ),
        "benefits6.svg": icon_svg(
            34,
            '<circle cx="10" cy="10" r="3"/><path d="M6 26l8-10 5 6 7-10"/>',
        ),
        "benefits7.svg": icon_svg(
            36,
            f'<ellipse cx="12" cy="8" rx="5" ry="2"/><path d="M7 8v12c0 1 2 2 5 2s5-1 5-2V8"/><circle cx="22" cy="20" r="6"/><text x="22" y="23" text-anchor="middle" font-size="7" fill="{g}" stroke="none" font-family="sans-serif">₩</text>',
        ),
        "benefits8.svg": icon_svg(
            33,
            f'<path d="M9 6h11l4 4v16H9z"/><path d="M20 6v4h4"/><line x1="12" y1="14" x2="22" y2="14"/><line x1="12" y1="18" x2="18" y2="18"/><line x1="12" y1="22" x2="22" y2="22"/><path d="M18 20l6 2v6l-3 2-3-2z" fill="none"/><path d="M20 25l1.5 1.5 3-3" stroke="{g}"/>',
        ),
        "talent1.svg": icon_svg(
            28,
            f'<line x1="8" y1="4" x2="8" y2="28" stroke="{g}" stroke-width="2"/><line x1="5" y1="28" x2="11" y2="28" stroke="{g}" stroke-width="2"/><path d="M8 5h12l-3 5 3 5H8z" fill="{g}" stroke="none"/>',
        ),
        "talent2.svg": icon_svg(
            26,
            f'<circle cx="16" cy="12" r="8" fill="none"/><path d="M20 8a6 6 0 0 1 0 8" stroke="{g}" stroke-width="1.4"/><rect x="13" y="20" width="6" height="4" fill="{g}" stroke="none"/><rect x="14" y="24" width="4" height="2" fill="{g}" stroke="none"/>',
        ),
        "talent3.svg": icon_svg(
            36,
            f'<path d="M6 22c0-8 6-14 14-14h2c6 0 10 4 10 10v2c0 4-3 8-8 8H14l-8 4v-10z" fill="{g}" stroke="none"/><circle cx="14" cy="18" r="2" fill="#333" stroke="none"/><circle cx="22" cy="18" r="2" fill="#333" stroke="none"/>',
        ),
        "talent4.svg": icon_svg(
            37,
            f'<path d="M4 14h8l6 4 6-4h8v4l-8 3v3l-6 4-6-4v-3l-8-3z" fill="none" stroke="{g}" stroke-width="2"/><path d="M14 21l2 2 2-1 2 1 2-2" stroke="{g}" stroke-width="1.5"/>',
        ),
        "recruit1.svg": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="42" height="40" viewBox="0 0 42 40">
  <path d="M10 4h18l6 6v26H10z" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M28 4v6h6" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="14" x2="28" y2="14" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="20" x2="28" y2="20" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="26" x2="24" y2="26" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M24 28l12 8" stroke="{blue}" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M33 33l3 5 2-1" fill="{blue}" stroke="none"/>
</svg>
''',
        "recruit2.svg": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="42" height="40" viewBox="0 0 42 40">
  <path d="M10 4h18l6 6v26H10z" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M28 4v6h6" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="14" x2="28" y2="14" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="20" x2="26" y2="20" stroke="#a0a0a0" stroke-width="2"/>
  <line x1="14" y1="26" x2="22" y2="26" stroke="#a0a0a0" stroke-width="2"/>
  <circle cx="28" cy="28" r="7" fill="none" stroke="{blue}" stroke-width="2.2"/>
  <line x1="33" y1="33" x2="38" y2="38" stroke="{blue}" stroke-width="2.2" stroke-linecap="round"/>
</svg>
''',
        "recruit3.svg": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="42" height="40" viewBox="0 0 42 40">
  <circle cx="21" cy="12" r="8" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M7 36c2-10 26-10 28 0" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M19 22h4l2 4-4 10-4-10z" fill="{blue}" stroke="none"/>
</svg>
''',
        "recruit4.svg": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="43" height="35" viewBox="0 0 43 35">
  <path d="M21.5 4c4 0 12 7 12 14 0 8-8 13-12 13S9.5 26 9.5 18C9.5 11 17.5 4 21.5 4z" fill="none" stroke="#a0a0a0" stroke-width="2"/>
  <path d="M6 18h10l3-8 3 14 3-6h12" fill="none" stroke="{blue}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    }
    for name, content in icons.items():
        write(RESP / "contents" / name, content)


def build_ui_icons() -> None:
    # Pagination chevrons
    write(
        RESP / "common" / "btn_board_first.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" viewBox="0 0 16 12">
  <path d="M7 1L2 6l5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M13 1L8 6l5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    )
    write(
        RESP / "common" / "btn_board_pre.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="12" viewBox="0 0 10 12">
  <path d="M8 1L3 6l5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    )
    write(
        RESP / "common" / "btn_board_next.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="12" viewBox="0 0 10 12">
  <path d="M2 1l5 5-5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    )
    write(
        RESP / "common" / "btn_board_last.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" viewBox="0 0 16 12">
  <path d="M3 1l5 5-5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M9 1l5 5-5 5" fill="none" stroke="#555" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    )
    write(
        RESP / "common" / "ico-down.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="12" viewBox="0 0 10 12">
  <path d="M5 1v7M2 6l3 3 3-3" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''',
    )
    # Search button
    ko = text_paths("검색", FONT_BOLD, 12, 26, 18, "#fff", anchor="middle")
    write(
        RESP / "common" / "btn_search.svg",
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="52" height="26" viewBox="0 0 52 26" role="img" aria-label="검색">
  <defs>
    <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#5a7a9a"/>
      <stop offset="100%" stop-color="#2a3a4a"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="51" height="25" rx="3" fill="url(#sg)" stroke="#1a2a3a"/>
  {ko}
</svg>
''',
    )
    # FAQ button
    ko = text_paths("질문하기", FONT_BOLD, 13, 48, 22, "#fff", anchor="middle")
    write(
        RESP / "customer" / "btn_faq.svg",
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="96" height="32" viewBox="0 0 96 32" role="img" aria-label="질문하기">
  <defs>
    <linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#5cbadd"/>
      <stop offset="100%" stop-color="#3a8fb0"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="95" height="31" rx="4" fill="url(#fg)" stroke="#2f7a98"/>
  {ko}
</svg>
''',
    )
    # Safety report pill (unused in responsive but convert for completeness if present)
    src = RESP / "main" / "m-newspaper.png"
    if src.exists():
        ko = text_paths("안전신문고", FONT_BOLD, 11, 52, 16, "#fff", anchor="middle")
        write(
            RESP / "main" / "m-newspaper.svg",
            f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="104" height="24" viewBox="0 0 104 24" role="img" aria-label="안전신문고">
  <rect width="104" height="24" rx="12" fill="#f37021"/>
  {ko}
</svg>
''',
        )
    # PDF icon
    write(
        RESP / "common" / "ico_pdf.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" role="img" aria-label="PDF">
  <path d="M3 1h7l3 3v11H3z" fill="#fff" stroke="#bbb" stroke-width="0.8"/>
  <path d="M10 1v3h3" fill="#eee" stroke="#bbb" stroke-width="0.8"/>
  <rect x="3" y="1" width="10" height="4" fill="#e53935"/>
  <text x="8" y="4.2" text-anchor="middle" font-size="3.2" fill="#fff" font-family="Arial,sans-serif" font-weight="700">PDF</text>
  <path d="M5 9c2-3 6-1 5 2-2 1-5 1-5-2z" fill="#e53935"/>
</svg>
''',
    )
    # Hangul file icon
    write(
        RESP / "commom" / "ico_han.svg",
        '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" role="img" aria-label="한글">
  <path d="M3 1h7l3 3v11H3z" fill="#fff" stroke="#bbb" stroke-width="0.8"/>
  <path d="M10 1v3h3" fill="#eee" stroke="#bbb" stroke-width="0.8"/>
  <rect x="3" y="1" width="10" height="4" fill="#2f6fbf"/>
  <text x="8" y="4.2" text-anchor="middle" font-size="3.4" fill="#fff" font-family="sans-serif" font-weight="700">한</text>
  <text x="8" y="11" text-anchor="middle" font-size="5" fill="#2f6fbf" font-family="sans-serif">가</text>
</svg>
''',
    )


def build_quick_menu_svgs() -> None:
    """Convert unused-but-suitable quick menu icons for inventory completeness."""
    items = [
        ("quick_menu01.svg", "공지사항", '<rect x="18" y="2" width="14" height="22" rx="3" fill="none" stroke="#777" stroke-width="2"/><rect x="22" y="6" width="6" height="10" rx="3" fill="none" stroke="#777" stroke-width="1.6"/><path d="M20 24h10" stroke="#777" stroke-width="2"/><path d="M25 24v4" stroke="#777" stroke-width="2"/>'),
        ("quick_menu02.svg", "입찰공고", '<rect x="14" y="8" width="22" height="24" rx="2" fill="none" stroke="#777" stroke-width="2"/><path d="M20 4h10v6H20z" fill="#777"/><circle cx="19" cy="16" r="1.2" fill="#777"/><circle cx="19" cy="21" r="1.2" fill="#777"/><circle cx="19" cy="26" r="1.2" fill="#777"/><line x1="23" y1="16" x2="32" y2="16" stroke="#777" stroke-width="1.5"/><line x1="23" y1="21" x2="32" y2="21" stroke="#777" stroke-width="1.5"/><line x1="23" y1="26" x2="30" y2="26" stroke="#777" stroke-width="1.5"/>'),
        ("quick_menu03.svg", "열공급규정", '<path d="M24 4c0 0-6 0-6 8v6a6 6 0 0 0 12 0v-6c0-8-6-8-6-8z" fill="none" stroke="#777" stroke-width="2"/><circle cx="24" cy="26" r="5" fill="none" stroke="#777" stroke-width="2"/><line x1="30" y1="10" x2="34" y2="10" stroke="#777" stroke-width="1.5"/><line x1="30" y1="14" x2="34" y2="14" stroke="#777" stroke-width="1.5"/><line x1="30" y1="18" x2="34" y2="18" stroke="#777" stroke-width="1.5"/>'),
        ("quick_menu04.svg", "연료금표", '<ellipse cx="20" cy="22" rx="7" ry="3" fill="none" stroke="#777" stroke-width="1.6"/><path d="M13 22v-8c0-1.5 3-3 7-3s7 1.5 7 3v8" fill="none" stroke="#777" stroke-width="1.6"/><ellipse cx="28" cy="18" rx="7" ry="3" fill="none" stroke="#777" stroke-width="1.6"/><path d="M21 18v-8c0-1.5 3-3 7-3s7 1.5 7 3v8" fill="none" stroke="#777" stroke-width="1.6"/>'),
    ]
    for fname, label, icon in items:
        t = text_paths(label, FONT_MED, 9, 24.5, 44, "#777", anchor="middle")
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="49" height="48" viewBox="0 0 49 48" role="img" aria-label="{label}">
  <g transform="translate(0,0)">{icon}</g>
  {t}
</svg>
'''
        write(RESP / "common" / fname, svg)


def main() -> None:
    assert FONT_BOLD.exists(), FONT_BOLD
    build_header_logo()
    build_footer_logo()
    build_concept_logos()
    build_section_titles()
    build_sitemap_labels()
    build_content_icons()
    build_ui_icons()
    build_quick_menu_svgs()
    build_traced_assets()
    print(f"Generated {len(CONVERTED)} SVG files")
    for rel, kind in CONVERTED:
        print(f"  [{kind}] {rel}")


if __name__ == "__main__":
    main()
