"""Verify the page geometrically: nothing spills its band, nothing collides.

Vision calls kept timing out on this page, so the checks here are the ones a
printed sheet would get: every text block and rule against the margins it must
respect, and every block's used height against the band it was given. It records
what the drawing actually emits rather than trusting a hand-written model of the
layout, so a change to draw.py is checked as it is, not as it was documented.

Run: python3 verify.py
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("d", "draw.py")
d = importlib.util.module_from_spec(spec)
sys.modules["d"] = d
spec.loader.exec_module(d)

TOL = 0.5          # a hair, in design units, for rounding at the half-scale
problems = []


class Probe(d.Page):
    """A Page that records every text block it draws, in design units."""

    def __init__(self):
        super().__init__()
        self.boxes = []

    def text(self, x, y, s, f, fill, anchor="la"):
        bb = self.d.textbbox((x * d.S, y * d.S), s, font=f, anchor=anchor)
        self.boxes.append(dict(
            x0=bb[0] / d.S, y0=bb[1] / d.S, x1=bb[2] / d.S, y1=bb[3] / d.S,
            text=s.replace("\n", " "), size=f.size / d.S,
        ))
        super().text(x, y, s, f, fill, anchor)


def check(boxes):
    # 1. nothing crosses the page margins (left bearing of italic type can sit a
    #    hair outside the origin, so the left edge gets a wider tolerance)
    for b in boxes:
        if b["x0"] < d.M - 1.5 or b["x1"] > d.W - d.M + TOL:
            problems.append(f"margin: x{b['x0']:.0f}-{b['x1']:.0f} {b['text'][:40]!r}")
        if b["y0"] < d.M - TOL or b["y1"] > d.H - 2:
            problems.append(f"margin: y{b['y0']:.0f}-{b['y1']:.0f} {b['text'][:40]!r}")

    # 2. no two text blocks overlap
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if not (a["x1"] <= b["x0"] + TOL or b["x1"] <= a["x0"] + TOL
                    or a["y1"] <= b["y0"] + TOL or b["y1"] <= a["y0"] + TOL):
                problems.append(
                    f"collision: {a['text'][:34]!r} at y{a['y0']:.0f}-{a['y1']:.0f} "
                    f"meets {b['text'][:34]!r} at y{b['y0']:.0f}-{b['y1']:.0f}")

    # 3. no block may cross the boundary between two bands
    bounds = [d.HEAD_RULE, d.GRID_Y, d.BRIEF_Y]
    for b in boxes:
        for edge in bounds:
            if b["y0"] < edge - 4 and b["y1"] > edge + 1:
                problems.append(
                    f"band boundary y{edge}: {b['text'][:38]!r} spans y{b['y0']:.0f}-{b['y1']:.0f}")

    # 4. the grid's rows must not run into each other
    for k in range(len(d.SECOND)):
        row = k // 4
        y0 = d.GRID_Y + row * d.GRID_ROW_H
        y1 = y0 + d.GRID_ROW_H
        here = [b for b in boxes if y0 - TOL <= b["y0"] < y1]
        low = max((b["y1"] for b in here), default=y0)
        if low > y1 - 2:
            problems.append(f"grid row {row}: lowest text y{low:.0f} reaches the row edge {y1}")


def main():
    p = Probe()
    for step in (d.draw_nameplate, d.draw_hero, d.draw_grid, d.draw_numbers, d.draw_briefs):
        step(p)

    check(p.boxes)

    print(f"text blocks recorded: {len(p.boxes)}")
    print(f"lowest block per band:")
    for name, y0, y1 in (("nameplate", 0, d.HEAD_RULE), ("hero", d.HEAD_RULE, d.GRID_Y),
                         ("grid", d.GRID_Y, d.BRIEF_Y), ("briefs", d.BRIEF_Y, d.H)):
        inside = [b["y1"] for b in p.boxes if y0 <= b["y0"] < y1]
        if inside:
            print(f"  {name:<10} y{max(inside):>6.0f}  (band ends {y1})")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for s in problems:
            print("  !!", s)
        return 1

    print("\nall geometry checks pass: no collisions, no overflow, no margin bleed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
