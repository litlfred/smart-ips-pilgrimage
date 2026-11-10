#!/usr/bin/env python3
"""Draw the overview of key process flows in the original figure's style, from the ArchiMate model.

Usage:
    python3 -I archimate/pretty.py           # write input/includes/workflow-pretty.svg
    python3 -I archimate/pretty.py --check   # fail if the committed drawing is stale

The ArchiMate view "Overview of key process flows" (archimate/build.py) is
the one source. This script reads it from the built model and draws it the
way input/images/workflow.png does: a pictogram per role instead of a typed
box, the two countries as large labels split by a dashed Y, and each flow as
an arrow with its number (blue) or letter (green) in a circle. Nothing is
typed here except how a role looks:

- every box is placed where the view places it;
- every pictogram is the role its element realises (the element's `role`
  property, scenarios/roles.json), labelled with the element's name (the IG's
  actor or persona) and linked to its page (the `page` property);
- every arrow is a Flow of the view, labelled with its name as the figure
  prints it, its circle linked to its journey moment, and its transaction
  code linked to IPS.HAJJ.TRANSACTION.

The archimate-pages visualiser draws the same view in ArchiMate notation; the
pages offer both, with a toggle. Standard library only.
"""

import html
import math
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "input/includes/workflow-pretty.svg"
IG = "https://litlfred.github.io/smart-ips-pilgrimage/"
VIEW = "Overview of key process flows"
XSI = "{http://www.w3.org/2001/XMLSchema-instance}type"
BLUE, BLUE_TEXT, GREEN, INK = "#4472C4", "#2F5597", "#548235", "#1f1f1f"
W, H = 1280, 760

# How each role looks: a pictogram drawn in a 64 x 64 box centred on (0, 0).
ICONS = {
    # a person in a pilgrim's ihram, the cloth over one shoulder
    "pilgrim": f'<circle cx="0" cy="-20" r="11" fill="{INK}"/>'
               f'<path d="M-24 30 Q-24 -2 0 -4 Q24 -2 24 30 Z" fill="{INK}"/>'
               '<path d="M-14 0 L16 30 L6 30 L-18 6 Z" fill="#fff"/>',
    # a clinician: head, shoulders, stethoscope
    "host-health-worker": f'<circle cx="0" cy="-20" r="11" fill="{INK}"/>'
                          f'<path d="M-24 30 Q-24 -2 0 -4 Q24 -2 24 30 Z" fill="{INK}"/>'
                          '<path d="M-9 -2 L-9 12 Q-9 20 0 20 Q9 20 9 12 L9 -2" fill="none" stroke="#fff" stroke-width="3"/>'
                          '<circle cx="9" cy="-2" r="3" fill="#fff"/>',
    # a phone showing a QR code
    "origin-wallet": f'<rect x="-18" y="-30" width="36" height="60" rx="6" fill="none" stroke="{INK}" stroke-width="4"/>'
                     f'<rect x="-11" y="-18" width="9" height="9" fill="{INK}"/><rect x="2" y="-18" width="9" height="9" fill="{INK}"/>'
                     f'<rect x="-11" y="-5" width="9" height="9" fill="{INK}"/><rect x="5" y="-2" width="4" height="4" fill="{INK}"/>'
                     f'<rect x="2" y="5" width="4" height="4" fill="{INK}"/><rect x="8" y="5" width="3" height="3" fill="{INK}"/>'
                     f'<circle cx="0" cy="22" r="2.5" fill="{INK}"/>',
    # a health information exchange: a hub with the systems it joins
    "origin-hie": '<rect x="-30" y="-4" width="60" height="10" rx="3" fill="#8a8a8a"/>'
                  '<text x="0" y="4" text-anchor="middle" font-size="6" fill="#fff" font-weight="700">FHIR Health Exchange</text>'
                  + "".join(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#8a8a8a" stroke-width="3"/>'
                            f'<rect x="{x - 7}" y="{y2 - (12 if y2 < 0 else 0)}" width="14" height="12" rx="2" fill="#b0b0b0"/>'
                            for x in (-22, 0, 22) for y1, y2 in ((-4, -22), (6, 22)))
                  + '<text x="0" y="-26" text-anchor="middle" font-size="13" font-weight="800" fill="#c00030">IPS</text>',
    # a laptop showing a record
    "host-emr": f'<rect x="-26" y="-24" width="52" height="34" rx="3" fill="none" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M-34 14 L34 14 L30 22 L-30 22 Z" fill="{INK}"/>'
                f'<circle cx="-12" cy="-7" r="8" fill="{INK}"/><path d="M-12 -12 V-2 M-17 -7 H-7" stroke="#fff" stroke-width="2.5"/>'
                f'<path d="M0 -14 H18 M0 -7 H18 M0 0 H18" stroke="{INK}" stroke-width="2.5"/>',
    # WHO GDHCN: a network of trusted nodes around a key holder
    "trust-network": '<circle cx="-22" cy="-20" r="7" fill="none" stroke="#f0a500" stroke-width="3.5"/>'
                     '<circle cx="20" cy="-22" r="4" fill="none" stroke="#2bb5e8" stroke-width="2.5"/>'
                     '<circle cx="-26" cy="8" r="4" fill="none" stroke="#2bb5e8" stroke-width="2.5"/>'
                     '<circle cx="-18" cy="26" r="4" fill="none" stroke="#2bb5e8" stroke-width="2.5"/>'
                     '<circle cx="18" cy="12" r="7" fill="none" stroke="#f0a500" stroke-width="3.5"/>'
                     '<path d="M-22 -20 L18 12 M-26 8 L18 12" stroke="#c8c8c8" stroke-width="1.5"/>'
                     f'<circle cx="0" cy="-6" r="9" fill="none" stroke="{INK}" stroke-width="2"/>'
                     f'<path d="M-9 -6 H9 M0 -15 V3" stroke="{INK}" stroke-width="1.2"/>'
                     f'<path d="M-6 6 h12 v22 h-12 Z" fill="{INK}"/>',
}


def esc(s):
    return html.escape(str(s), quote=True)


def version():
    return re.search(r"^version:\s*(\S+)", (ROOT / "sushi-config.yaml").read_text(encoding="utf-8"), re.M).group(1)


def rel_link(url):
    """A link inside this guide is written relative, so a branch preview keeps it."""
    return url[len(IG):] if url.startswith(IG) else url


def read():
    path = ROOT / "archimate" / version() / "smart-ips-pilgrimage.archimate"
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("model.xml"))
    elements, rels = {}, {}
    for e in root.iter("element"):
        t = e.get(XSI, "").replace("archimate:", "")
        props = {p.get("key"): p.get("value") for p in e.findall("property")}
        if t.endswith("Relationship"):
            rels[e.get("id")] = (t[:-len("Relationship")], e.get("source"), e.get("target"), e.get("name") or "", props)
        elif t != "ArchimateDiagramModel":
            elements[e.get("id")] = (t, e.get("name"), props)
    view = next(e for e in root.iter("element") if e.get(XSI) == "archimate:ArchimateDiagramModel" and e.get("name") == VIEW)
    boxes, lines = {}, []

    def walk(node, ox, oy):
        for c in node.findall("child"):
            b = c.find("bounds")
            x, y = ox + int(b.get("x")), oy + int(b.get("y"))
            boxes[c.get("id")] = (c.get("archimateElement"), x, y, int(b.get("width")), int(b.get("height")))
            for sc in c.findall("sourceConnection"):
                lines.append((sc.get("archimateRelationship"), sc.get("source"), sc.get("target")))
            walk(c, x, y)

    walk(view, 0, 0)
    return elements, rels, boxes, lines


def clip(cx, cy, tx, ty, w, h, gap):
    """Where the line from a box's centre towards (tx, ty) leaves the box, plus a gap."""
    dx, dy = tx - cx, ty - cy
    s = min((w / 2) / abs(dx) if dx else math.inf, (h / 2) / abs(dy) if dy else math.inf)
    d = math.hypot(dx, dy)
    return cx + dx * s + dx / d * gap, cy + dy * s + dy / d * gap


def draw():
    elements, rels, boxes, lines = read()
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="wf-title" '
           f'style="width:100%;height:auto;font-family:Helvetica,Arial,sans-serif">',
           f'<title id="wf-title">{esc(VIEW)}</title>',
           "<!-- Generated by archimate/pretty.py from the ArchiMate view of the same name. Do not edit; edit archimate/build.py and rerun both. -->",
           f'<defs><marker id="wf-a-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{BLUE}"/></marker>'
           f'<marker id="wf-a-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{GREEN}"/></marker></defs>',
           '<rect width="100%" height="100%" fill="#fff"/>']

    # The countries: a dashed Y between them, and each one's name, large, at its outer edge.
    locs = [(elements[e][1], x, y, w, h) for e, x, y, w, h in boxes.values() if elements[e][0] == "Location"]
    gdhcn = next((b for b in boxes.values() if elements[b[0]][2].get("role", "").endswith("#trust-network")), None)
    fork_y = gdhcn[2] - 150 if gdhcn else H - 260
    out.append(f'<path d="M{W / 2} 30 V{fork_y} M{W / 2} {fork_y} L{W / 2 - 330} {H - 10} M{W / 2} {fork_y} L{W / 2 + 330} {H - 10}" '
               'stroke="#a9bde6" stroke-width="3" stroke-dasharray="10 8" fill="none"/>')
    for name, x, y, w, h in locs:
        left = x + w / 2 < W / 2
        tx = x + 20 if left else x + w - 20
        words = name.split()
        lines_ = [" ".join(words[: len(words) // 2 or 1]), " ".join(words[len(words) // 2 or 1:])] if len(words) > 1 else words
        out.append(f'<text x="{tx}" y="{y + h * 0.66}" text-anchor="{"start" if left else "end"}" font-size="30" font-weight="700" fill="{BLUE}">'
                   + "".join(f'<tspan x="{tx}" dy="{0 if i == 0 else 34}">{esc(t)}</tspan>' for i, t in enumerate(l for l in lines_ if l))
                   + "</text>")

    # The roles: a pictogram each, named as the IG names the actor or persona, linked to its page.
    centre = {}
    for oid, (eid, x, y, w, h) in boxes.items():
        t, name, props = elements[eid]
        if t == "Location":
            continue
        role = props.get("role", "").split("#")[-1]
        cx, cy = x + w / 2, y + h / 2
        # what an arrow keeps clear of: the pictogram and its two lines of label below it
        centre[oid] = (cx, cy + 16, max(w, 150), h + 56)
        colour = GREEN if role == "trust-network" else INK
        rows = textwrap.wrap(name, 22)
        label = "".join(f'<tspan x="{cx}" dy="{0 if i == 0 else 14}">{esc(t)}</tspan>' for i, t in enumerate(rows))
        actor = props.get("igActor")
        sub = (f'<text x="{cx}" y="{cy + (48 if role == "trust-network" else 40) + 14 * len(rows)}" text-anchor="middle" font-size="10.5" font-style="italic" fill="#666">'
               f'{esc(actor)} · role {esc(role)}</text>') if actor else (
               f'<text x="{cx}" y="{cy + (48 if role == "trust-network" else 40) + 14 * len(rows)}" text-anchor="middle" font-size="10.5" font-style="italic" fill="#666">role {esc(role)}</text>')
        body = (f'<g transform="translate({cx} {cy - 8}) scale({1.35 if role == "trust-network" else 1})">{ICONS.get(role, "")}</g>'
                f'<text x="{cx}" y="{cy + (48 if role == "trust-network" else 40)}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{colour}">{label}</text>{sub}')
        page = props.get("page")
        tip = f"<title>{esc(name)} (role {esc(role)}, scenarios/roles.json)</title>"
        out.append(f'<a href="{esc(rel_link(page))}" target="_top">{tip}{body}</a>' if page else f"<g>{tip}{body}</g>")

    # The flows: an arrow each, with its step in a circle and its label as printed.
    for rid, s, t in lines:
        kind, _, _, name, props = rels[rid]
        if kind != "Flow" or s not in centre or t not in centre:
            continue
        step = props.get("step", "")
        green = step.isalpha()
        colour, text_colour = (GREEN, GREEN) if green else (BLUE, BLUE_TEXT)
        (sx, sy, sw, sh), (tx, ty, tw, th) = centre[s], centre[t]
        x1, y1 = clip(sx, sy, tx, ty, sw, sh, 10)
        x2, y2 = clip(tx, ty, sx, sy, tw, th, 10)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-width="2.5" '
                   f'marker-end="url(#wf-a-{"green" if green else "blue"})"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        moment = props.get("journeyMoment")
        circle = (f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="15" fill="#fff" stroke="{colour}" stroke-width="2.5"/>'
                  f'<text x="{mx:.1f}" y="{my + 6:.1f}" text-anchor="middle" font-size="17" font-weight="700" fill="{colour}">{esc(step)}</text>')
        out.append(f'<a href="{esc(rel_link(moment))}" target="_top"><title>Step {esc(step)}: its moment of the pilgrim\'s journey</title>{circle}</a>'
                   if moment else circle)
        # The label sits beside the arrow: above it, or for a lettered flow on the side away from the middle.
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        nx, ny = -dy / d, dx / d
        if green:
            if (nx < 0) != (mx < W / 2):
                nx, ny = -nx, -ny
        elif ny > 0 or (abs(ny) < 1e-6 and nx > 0):
            nx, ny = -nx, -ny
        text = re.sub(r"^\w+\.\s*", "", name)
        wrapped = textwrap.wrap(text, 38)
        tx_ = props.get("transaction")
        code = tx_.split("TRANSACTION-")[-1] if tx_ else None
        rows = len(wrapped) + (1 if code else 0)
        lx = mx + nx * 48
        # the block's near edge sits 26px from the arrow; first baseline 12px below its top
        ly = my + ny * 26 + 12 - (rows * 16 if ny < -0.3 else 0 if ny > 0.3 else rows * 8)
        anchor = "middle" if abs(nx) < 0.5 else ("start" if nx > 0 else "end")
        lab = "".join(f'<tspan x="{lx:.1f}" dy="{0 if i == 0 else 16}">{esc(w_)}</tspan>' for i, w_ in enumerate(wrapped))
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="13.5" fill="{text_colour}">{lab}</text>')
        if code:
            cy_ = ly + 16 * len(wrapped)
            out.append(f'<a href="{esc(rel_link(tx_))}" target="_top"><title>Transaction {esc(code)} (IPS.HAJJ.TRANSACTION)</title>'
                       f'<text x="{lx:.1f}" y="{cy_:.1f}" text-anchor="{anchor}" font-size="11" fill="{text_colour}" font-style="italic">{esc(code)}</text></a>')
    out.append("</svg>\n")
    return "\n".join(out)


def main(argv):
    svg = draw()
    rel = OUT.relative_to(ROOT)
    if "--check" in argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != svg:
            print(f"{rel}: stale; run python3 -I archimate/pretty.py", file=sys.stderr)
            return 1
        print(f"{rel}: current")
        return 0
    OUT.write_text(svg, encoding="utf-8")
    print(f"{rel}: written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
