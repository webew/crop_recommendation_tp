"""Petits outils pour dessiner les schémas du guide en SVG (boîtes, flèches, textes)."""

from html import escape

FOREST = "#2C5F2D"
MOSS = "#97BC62"
MOSS_BG = "#EEF4E6"
WHEAT = "#B7791F"
WHEAT_BG = "#FBF1DF"
INK = "#1F2A1F"
GREY = "#5B6B5B"
LINE = "#C9D3C4"
RED = "#B5452B"
RED_BG = "#F8E6E1"
BLUE = "#2F5D7C"
BLUE_BG = "#E5EEF4"
WHITE = "#FFFFFF"

STYLES = {
    "main": (FOREST, FOREST, WHITE),
    "soft": (MOSS_BG, MOSS, INK),
    "file": (WHITE, LINE, INK),
    "wheat": (WHEAT_BG, WHEAT, INK),
    "red": (RED_BG, RED, INK),
    "blue": (BLUE_BG, BLUE, INK),
    "ghost": ("none", "none", GREY),
}


def text(x, y, s, size=13, color=INK, weight="normal", anchor="middle", mono=False, italic=False):
    family = "Menlo, monospace" if mono else "'Helvetica Neue', Arial, sans-serif"
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{style}>{escape(s)}</text>'
    )


def box(x, y, w, h, title, sub=None, style="soft", size=14, sub_size=11.5, rx=10, mono_sub=True, dashed=False):
    fill, stroke, color = STYLES[style]
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>']
    title_lines = title.split("\n")
    sub_lines = sub.split("\n") if sub else []
    line_h_t = size * 1.25
    line_h_s = sub_size * 1.35
    total = len(title_lines) * line_h_t + len(sub_lines) * line_h_s + (4 if sub_lines else 0)
    cy = y + (h - total) / 2 + size * 0.95
    for t in title_lines:
        out.append(text(x + w / 2, cy, t, size=size, color=color, weight="bold"))
        cy += line_h_t
    if sub_lines:
        cy += 4 - line_h_t + line_h_s
        sub_color = color if style == "main" else GREY
        if style == "main":
            sub_color = "#DCEBD0"
        for s in sub_lines:
            out.append(text(x + w / 2, cy, s, size=sub_size, color=sub_color, mono=mono_sub))
            cy += line_h_s
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label=None, color=GREY, dashed=False, label_dx=0, label_dy=-6, width=1.6, label_size=11):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    marker = {FOREST: "arrowF", WHEAT: "arrowW", RED: "arrowR", BLUE: "arrowB"}.get(color, "arrowG")
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dash} marker-end="url(#{marker})"/>']
    if label:
        mx, my = (x1 + x2) / 2 + label_dx, (y1 + y2) / 2 + label_dy
        out.append(text(mx, my, label, size=label_size, color=color if color != GREY else GREY, italic=True))
    return "\n".join(out)


def path_arrow(d, color=GREY, dashed=False, width=1.6):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    marker = {FOREST: "arrowF", WHEAT: "arrowW", RED: "arrowR", BLUE: "arrowB"}.get(color, "arrowG")
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash} marker-end="url(#{marker})"/>'


def rect(x, y, w, h, fill, stroke="none", rx=0, dashed=False, width=1.4):
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dash}/>'


def circle(cx, cy, r, fill, label=None, color=WHITE, size=13):
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
    if label is not None:
        out += text(cx, cy + size * 0.36, str(label), size=size, color=color, weight="bold")
    return out


def svg(w, h, *elements):
    defs = "".join(
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>'
        for mid, col in (("arrowG", GREY), ("arrowF", FOREST), ("arrowW", WHEAT), ("arrowR", RED), ("arrowB", BLUE))
    )
    body = "\n".join(elements)
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img"><defs>{defs}</defs>{body}</svg>'
