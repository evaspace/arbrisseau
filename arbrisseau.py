"""arbrisseau: binary and general trees as small SVG files, from nested tuples, with no dependency.

Binary tree: `(key, left, right)`, `None` for an empty subtree, a bare key for a leaf.
General tree: `(key, [children])`, a bare key for a leaf.
"""
import hashlib
import html
from pathlib import Path

__version__ = "0.1.0"
__all__ = ["svg", "save", "fcrs"]

STYLE = {"r": 14, "dx": 30, "dy": 46, "caption": 24, "wrap": 380,
         "font": "JetBrains Mono, Menlo, Consolas, monospace", "ink": "#111", "fill": "#fff"}


def _key(s):
    return s[0] if isinstance(s, tuple) else s


def _kids(s):
    return (s[1], s[2]) if isinstance(s, tuple) else (None, None)


def _gkids(g):
    return g[1] if isinstance(g, tuple) else []


def fcrs(forest):
    """First child - right sibling binary form of a forest (a list of general trees)."""
    if not forest:
        return None
    g = forest[0]
    left, right = fcrs(_gkids(g)), fcrs(forest[1:])
    return _key(g) if left is None and right is None else (_key(g), left, right)


def _bin_nodes(s, d, acc, edges):
    """In-order layout: each node gets its own column, so no two nodes ever overlap."""
    left, right = _kids(s)
    li = _bin_nodes(left, d + 1, acc, edges) if left is not None else None
    me = len(acc)
    acc.append((me, d, _key(s)))
    ri = _bin_nodes(right, d + 1, acc, edges) if right is not None else None
    edges += [(me, i) for i in (li, ri) if i is not None]
    return me


def _gen_nodes(g, d, acc, edges, cnt):
    """Leaves left to right, each parent centred over its children."""
    idx = len(acc)
    acc.append(None)
    cis = [_gen_nodes(c, d + 1, acc, edges, cnt) for c in _gkids(g)]
    if cis:
        x = (acc[cis[0]][0] + acc[cis[-1]][0]) / 2
    else:
        x, cnt[0] = cnt[0], cnt[0] + 1.25  # sibling leaves share a level: more room than in-order slots
    acc[idx] = (x, d, _key(g))
    edges += [(idx, c) for c in cis]
    return idx


def svg(*trees, captions=None, general=False, **style):
    """SVG text of one or more trees side by side, with an optional caption under each one.

    Trees wrap to a new row past `wrap` pixels (380 by default) so that a phone shows them near scale 1.
    """
    st = {**STYLE, **style}
    r, dx, dy, cap_h = st["r"], st["dx"], st["dy"], st["caption"]
    parts, x0, y0, row_h, width = [], 10, 10, 0, 0
    for s, cap in zip(trees, list(captions or []) + [None] * len(trees)):
        acc, edges = [], []
        if s is not None:
            (_gen_nodes(s, 0, acc, edges, [0]) if general else _bin_nodes(s, 0, acc, edges))
        w = max([dx, len(cap or "") * 9.5] + [(x + 1) * dx for x, _, _ in acc]) + 10  # 9.5 px per caption char
        shift = (w - 10 - max([dx] + [(x + 1) * dx for x, _, _ in acc])) / 2  # centre the tree under a long caption
        h = (max((d for _, d, _ in acc), default=0) + 1) * dy + (cap_h if cap else 0)
        if x0 > 10 and x0 + w > st["wrap"]:
            x0, y0, row_h = 10, y0 + row_h + 12, 0
        px = lambda i: x0 + shift + acc[i][0] * dx + dx / 2  # noqa: E731
        py = lambda i: y0 + acc[i][1] * dy + r + 4  # noqa: E731
        for a, b in edges:
            parts.append(f'<line x1="{px(a):.1f}" y1="{py(a):.1f}" x2="{px(b):.1f}" y2="{py(b):.1f}"/>')
        for i, (_, _, k) in enumerate(acc):
            label = "" if k is None else html.escape(str(k))
            parts.append(f'<circle cx="{px(i):.1f}" cy="{py(i):.1f}" r="{r}"/>'
                         f'<text x="{px(i):.1f}" y="{py(i) + 5:.1f}">{label}</text>')
        if not acc:
            parts.append(f'<text x="{x0 + w / 2:.1f}" y="{y0 + 22}">empty</text>')
        if cap:
            parts.append(f'<text class="c" x="{x0 + w / 2:.1f}" y="{y0 + h - 6:.1f}">{html.escape(cap)}</text>')
        x0 += w + 24
        row_h = max(row_h, h)
        width = max(width, x0)
    W, H = int(width - 14), int(y0 + row_h + 10)
    ink, fill = st["ink"], st["fill"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{st["font"]}" font-size="14" text-anchor="middle">'
            f'<style>line{{stroke:{ink};stroke-width:1.5}}circle{{fill:{fill};stroke:{ink};stroke-width:1.5}}'
            f'text{{fill:{ink}}}.c{{font-size:15px;font-weight:700}}</style>' + "".join(parts) + "</svg>")


def save(*trees, folder=".", prefix="tree-", captions=None, general=False, **style):
    """Write the SVG to `folder/<prefix><hash>.svg`; the same drawing keeps the same name. Returns the path."""
    text = svg(*trees, captions=captions, general=general, **style)
    path = Path(folder) / f"{prefix}{hashlib.sha1(text.encode()).hexdigest()[:12]}.svg"
    if not path.exists() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return path
