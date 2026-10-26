"""Glyco Atlas look for figures and console output (shared by the notebook and the report).

  style()            matplotlib theme: warm paper, ink text, vermilion accent, serif titles
  tbl(df)            print a DataFrame as a boxed, right-aligned text table
  rule(text)         print a section rule
  kv(dict)           print aligned key / value lines
"""
import re

import matplotlib as mpl
from matplotlib import font_manager

PAPER, PAPER2, PAPER3 = "#fbfaf7", "#f0eee9", "#e4e1da"
INK, INK_SOFT, INK_FAINT, RULE = "#141414", "#3d3d3d", "#5f5f5f", "#cfccc4"
ACCENT = "#c2321a"

# one colour per entity type (same hues as the website)
TYPE_COLORS = {"DiabetesType": "#b3301f", "Symptom": "#c26a14", "RiskFactor": "#7c5230",
               "Complication": "#7b4aa8", "Test": "#12809a", "Drug": "#2f5fd0", "DrugClass": "#5a7fd0",
               "Food": "#2b8a4e", "Lifestyle": "#8d8514", "Organ": "#c0407f"}
TYPE_ORDER = ["DiabetesType", "Symptom", "RiskFactor", "Lifestyle", "Food", "Test",
              "Complication", "Organ", "Drug", "DrugClass"]


def _first(candidates, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in candidates if c in have), fallback)


SERIF = _first(["Source Serif 4", "Cambria", "Palatino Linotype", "DejaVu Serif"], "serif")   # all cover Vietnamese
SANS = _first(["IBM Plex Sans", "Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"], "sans-serif")
MONO = _first(["IBM Plex Mono", "Consolas", "Menlo", "DejaVu Sans Mono"], "monospace")


def style():
    mpl.rcParams.update({
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "figure.dpi": 110, "savefig.dpi": 200,
        "font.family": SANS, "font.size": 9.5, "text.color": INK,
        "axes.edgecolor": INK, "axes.labelcolor": INK_SOFT, "axes.linewidth": 0.9,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": INK_FAINT, "ytick.color": INK_FAINT, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
        "axes.grid": True, "grid.color": RULE, "grid.linestyle": (0, (1, 3)), "grid.linewidth": 0.8,
        "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 8.5,
        "axes.prop_cycle": mpl.cycler(color=[ACCENT, INK, "#2f5fd0", "#2b8a4e", "#c26a14", "#7b4aa8"]),
    })


def title(ax, text, sub=None):
    """Serif title with an optional mono sub-title line, left-aligned like the website headings."""
    ax.set_title(text, fontfamily=SERIF, fontsize=14.5, fontweight="bold", loc="left", pad=22 if sub else 12)
    if sub:
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontfamily=MONO, fontsize=7.8, color=INK_FAINT, va="bottom")


# ---------------------------------------------------------------- console output
def rule(text="", width=88, char="━"):
    text = f" {text} " if text else ""
    print(f"\n{char * 3}{text}{char * max(3, width - 3 - len(text))}")


def kv(items, width=None):
    width = width or max(len(str(k)) for k in items)
    for k, v in items.items():
        print(f"  {str(k):<{width}} │ {v}")


def _cell(v, limit):
    if isinstance(v, (list, tuple)):
        v = " · ".join(map(str, v))
    if isinstance(v, float):
        v = f"{v:.3f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))
    s = "" if v is None or (isinstance(v, float) and v != v) else str(v)
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= limit else s[: limit - 1] + "…"


def tbl(df, title=None, limit=44, index=False, note=None):
    """Print a DataFrame as a boxed text table; numbers right-aligned, long cells truncated."""
    d = df.reset_index() if index else df
    cols = [str(c) for c in d.columns]
    rows = [[_cell(v, limit) for v in r] for r in d.itertuples(index=False)]
    numeric = [bool(len(d)) and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in d[c])
               for c in d.columns]
    w = [max([len(c)] + [len(r[i]) for r in rows]) for i, c in enumerate(cols)]

    def line(l, m, r, f="─"):
        return l + m.join(f * (x + 2) for x in w) + r

    def fmt(cells, head=False):
        out = []
        for i, c in enumerate(cells):
            out.append(f" {c:>{w[i]}} " if numeric[i] and not head else f" {c:<{w[i]}} ")
        return "│" + "│".join(out) + "│"

    if title:
        print(f"\n▎{title}")
    print(line("┌", "┬", "┐"))
    print(fmt([c.upper() for c in cols], head=True))
    print(line("├", "┼", "┤"))
    for r in rows:
        print(fmt(r))
    print(line("└", "┴", "┘"))
    print(f"  {len(d)} row{'s' if len(d) != 1 else ''}" + (f"  ·  {note}" if note else ""))
