"""Draw the diabetes KG in the "Glyco Atlas" style (used by the notebook and the report).

Instead of force-directed hairballs the drawings use layouts that stay readable:

  draw_ring        whole graph on a ring, grouped by entity type, facts as curved chords
  draw_ego         one entity in the middle, its neighbours on a ring grouped by relation
  draw_schema      entity types as boxes, facts as ribbons whose width is the number of facts
  draw_arcs        drugs on a line: arcs above = "treats type 2", arcs below = side effects
  draw_toy         the 7-fact teaching graph, left to right
  bubble_matrix    count per (row, column) as a bubble
  lollipop         ranking with diamond heads
  unit_chart       one diamond per entity, one row per type
  ecdf             cumulative curve with quantile marks

  python kg/visualize.py   ->  report/images/ring.png and ego_type2.png
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
if "ipykernel" not in sys.modules:       # scripts draw to files; Jupyter keeps its inline backend
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, PathPatch, Wedge
from matplotlib.path import Path as MPath

import atlas
from atlas import ACCENT, INK, INK_FAINT, INK_SOFT, MONO, PAPER, RULE, SERIF, TYPE_COLORS, TYPE_ORDER

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed"
FIG = ROOT / "report" / "images"
COLORS = TYPE_COLORS

REL_OUT = {"HAS_SYMPTOM": "Symptoms", "HAS_RISK_FACTOR": "Risk factors", "HAS_COMPLICATION": "Complications",
           "DIAGNOSED_BY": "Diagnosed with", "TREATED_BY": "Treated with", "MANAGED_BY": "Managed by",
           "RECOMMENDS_FOOD": "Recommended foods", "AVOIDS_FOOD": "Foods to avoid", "HAS_SIDE_EFFECT": "Side effects",
           "BELONGS_TO_CLASS": "Drug class", "AFFECTS_ORGAN": "Affects organ", "SUBTYPE_OF": "Subtype of"}
REL_IN = {"HAS_SYMPTOM": "Symptom of", "HAS_RISK_FACTOR": "Risk factor for", "HAS_COMPLICATION": "Complication of",
          "DIAGNOSED_BY": "Used to diagnose", "TREATED_BY": "Used to treat", "MANAGED_BY": "Helps manage",
          "RECOMMENDS_FOOD": "Recommended for", "AVOIDS_FOOD": "To avoid with", "HAS_SIDE_EFFECT": "Side effect of",
          "BELONGS_TO_CLASS": "Drugs in class", "AFFECTS_ORGAN": "Damaged by", "SUBTYPE_OF": "Subtypes"}


def build_graph():
    G = nx.DiGraph()
    with open(DATA / "entities.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            G.add_node(r["name"], type=r["label"])
    with open(DATA / "triples.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            G.add_edge(r["subject"], r["object"], relation=r["relation"], support=int(r["support"]), source=r["source"])
    return G


def short(s, n=26):
    return s if len(s) <= n else s[: n - 1] + "…"


def _canvas(size, lim):
    atlas.style()
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def _chord(ax, p, q, k, **kw):
    mid = ((p[0] + q[0]) / 2 * k, (p[1] + q[1]) / 2 * k)
    ax.add_patch(PathPatch(MPath([p, mid, q], [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3]), fill=False, **kw))


def _radial_label(ax, theta, r, text, size=6.6, color=INK_SOFT, **kw):
    flip = math.cos(theta) < 0
    ax.text(r * math.cos(theta), r * math.sin(theta), text, fontsize=size, color=color, va="center",
            ha="right" if flip else "left", rotation=math.degrees(theta) + (180 if flip else 0),
            rotation_mode="anchor", **kw)


def _sector(ax, t0, t1, r, color, label, label_r, size=7.4):
    ax.add_patch(Wedge((0, 0), r + 0.014, math.degrees(t0), math.degrees(t1), width=0.014, color=color, lw=0))
    mid = (t0 + t1) / 2
    ax.text(label_r * math.cos(mid), label_r * math.sin(mid), label.upper(), fontsize=size, fontfamily=MONO,
            color=color, ha="center", va="center", fontweight="bold")


# ---------------------------------------------------------------- whole graph on a ring
def draw_ring(G, path=None, size=(13, 13)):
    fig, ax = _canvas(size, 1.95)
    groups = defaultdict(list)
    for n, d in G.nodes(data=True):
        groups[d["type"]].append(n)
    order = [t for t in TYPE_ORDER if t in groups]
    total = sum(len(v) for v in groups.values()) + 0.9 * len(order)
    gap = 0.9 * 2 * math.pi / total
    step = 2 * math.pi / total
    theta, spans, a = {}, {}, math.pi / 2
    for t in order:
        start = a
        for n in sorted(groups[t], key=lambda x: -G.degree(x)):
            theta[n] = a
            a -= step
        spans[t] = (a + step - 0.0, start + step * 0.0)
        a -= gap
    pos = {n: (math.cos(t), math.sin(t)) for n, t in theta.items()}
    for u, v, d in sorted(G.edges(data=True), key=lambda e: e[2]["support"]):
        lw = 0.5 + 0.3 * math.log1p(d["support"])
        _chord(ax, pos[u], pos[v], 0.12, color=TYPE_COLORS[G.nodes[u]["type"]], alpha=0.30 if d["source"] != "curated" else 0.5,
               lw=lw, ls="-" if d["source"] != "curated" else (0, (2, 2)))
    for n, (x, y) in pos.items():
        ax.scatter([x], [y], s=26 + 15 * G.degree(n), marker="D", color=TYPE_COLORS[G.nodes[n]["type"]], edgecolor=PAPER, lw=0.8, zorder=3)
        _radial_label(ax, theta[n], 1.045 + 0.0035 * G.degree(n), short(n), size=6.7, color=INK)
    for t, (lo, hi) in spans.items():
        _sector(ax, lo - step * 0.35, hi + step * 0.35, 1.68, TYPE_COLORS[t], t, 1.80)
    box = dict(boxstyle="square,pad=0.25", fc=PAPER, ec="none", alpha=0.9)
    ax.text(0, 0.06, f"{G.number_of_nodes()} entities", ha="center", fontfamily=SERIF, fontsize=17, fontweight="bold", bbox=box, zorder=6)
    ax.text(0, -0.06, f"{G.number_of_edges()} facts · chords coloured by their source type", ha="center", fontfamily=MONO, fontsize=7.5,
            color=INK_FAINT, bbox=box, zorder=6)
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


# ---------------------------------------------------------------- one entity and its neighbours
def draw_ego(G, center, path=None, size=(13, 13), label_size=6.8):
    fig, ax = _canvas(size, 1.95)
    groups = defaultdict(list)
    for u, v, d in G.out_edges(center, data=True):
        groups[(REL_OUT[d["relation"]], d["relation"])].append((v, d))
    for u, v, d in G.in_edges(center, data=True):
        groups[(REL_IN[d["relation"]], d["relation"])].append((u, d))
    keys = sorted(groups, key=lambda k: -len(groups[k]))
    total = sum(len(v) for v in groups.values()) + 1.2 * len(keys)
    step = 2 * math.pi / total
    a = math.pi / 2
    for k in keys:
        start = a
        for n, d in sorted(groups[k], key=lambda x: -x[1]["support"]):
            x, y = math.cos(a), math.sin(a)
            col = TYPE_COLORS[G.nodes[n]["type"]]
            ax.plot([0.07 * x, 0.96 * x], [0.07 * y, 0.96 * y], color=col, lw=0.5 + 0.3 * math.log1p(d["support"]), alpha=0.35, zorder=1)
            ax.scatter([x], [y], s=34 + 7 * min(d["support"], 40), marker="D", color=col, edgecolor=PAPER, lw=0.8, zorder=3)
            _radial_label(ax, a, 1.05, short(n, 30), size=label_size, color=INK)
            a -= step
        _sector(ax, a + step * 0.6, start + step * 0.4, 1.58, INK, f"{k[0]} · {len(groups[k])}", 1.72, size=7.2)
        a -= 1.2 * step
    ctype = G.nodes[center]["type"]
    ax.scatter([0], [0], s=1500, marker="D", color=TYPE_COLORS[ctype], edgecolor=PAPER, lw=2, zorder=4)
    ax.text(0, -0.17, short(center, 34), ha="center", fontfamily=SERIF, fontsize=14, fontweight="bold", zorder=5)
    ax.text(0, -0.25, ctype.upper(), ha="center", fontfamily=MONO, fontsize=7, color=INK_FAINT, zorder=5)
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


# ---------------------------------------------------------------- schema as ribbons
SCHEMA_COLS = {"DiabetesType": 0, "Symptom": 1, "RiskFactor": 1, "Lifestyle": 1, "Food": 1, "Test": 1,
               "Complication": 1, "Drug": 1, "Organ": 2, "DrugClass": 2}


def draw_schema(pairs, path=None, size=(13, 8.6)):
    """pairs: {(src_type, dst_type): (n_facts, 'REL (n) + REL (n)')}"""
    atlas.style()
    fig, ax = plt.subplots(figsize=size)
    ax.axis("off")
    ax.set_xlim(-0.5, 10.7); ax.set_ylim(-0.2, 10)
    cross = {k: v for k, v in pairs.items() if SCHEMA_COLS[k[0]] != SCHEMA_COLS[k[1]]}
    inner = {k: v for k, v in pairs.items() if SCHEMA_COLS[k[0]] == SCHEMA_COLS[k[1]] and k[0] != k[1]}
    k = 0.026
    outs, ins = defaultdict(float), defaultdict(float)
    for (s, d), (n, _) in cross.items():
        outs[s] += n; ins[d] += n
    x_of = {0: 0.0, 1: 4.7, 2: 9.0}
    width = 1.7
    mid_order = ["Symptom", "RiskFactor", "Lifestyle", "Food", "Test", "Complication", "Drug"]
    right_order = ["Organ", "DrugClass"]
    height = {t: max(outs[t], ins[t], 6) * k for t in outs.keys() | ins.keys()}
    y, box = 9.7, {}
    for col, names in ((0, ["DiabetesType"]), (1, mid_order), (2, right_order)):
        y = 9.7 if col != 0 else 9.7
        gap = 0.28 if col else 0
        total = sum(height[t] for t in names) + gap * (len(names) - 1)
        y = 4.9 + total / 2 if col == 0 else 9.7 - (0 if col == 1 else 1.2)
        for t in names:
            box[t] = (x_of[col], y - height[t], height[t]); y -= height[t] + gap
    off_o, off_i = defaultdict(float), defaultdict(float)
    for (s, d), (n, label) in sorted(cross.items(), key=lambda kv: (list(box).index(kv[0][1]), -kv[1][0])):
        th = n * k
        x0, ybot, h = box[s]; y0 = ybot + h - off_o[s] - th; off_o[s] += th
        x1, ybot1, h1 = box[d]; y1 = ybot1 + h1 - off_i[d] - th; off_i[d] += th
        xa, xb = x0 + width, x1
        verts = [(xa, y0), ((xa + xb) / 2, y0), ((xa + xb) / 2, y1), (xb, y1), (xb, y1 + th), ((xa + xb) / 2, y1 + th),
                 ((xa + xb) / 2, y0 + th), (xa, y0 + th), (xa, y0)]
        codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(verts, codes), color=TYPE_COLORS[d], alpha=0.30, lw=0))
        ax.text((xa + xb) / 2, (y0 + y1 + th) / 2, f"{label}", fontsize=6.4, fontfamily=MONO, color=INK,
                va="center", ha="center", bbox=dict(boxstyle="square,pad=0.12", fc=PAPER, ec="none", alpha=0.85))
    for t, (x, yb, h) in box.items():
        ax.add_patch(FancyBboxPatch((x, yb), width, h, boxstyle="square,pad=0", fc=TYPE_COLORS[t], ec="none"))
        ax.text(x + width / 2, yb + h / 2, t, ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    extra = "  ·  ".join(f"{label} {s}→{d}" for (s, d), (n, label) in inner.items()) + "  ·  SUBTYPE_OF (4) DiabetesType→DiabetesType"
    fig.text(0.01, 0.985, "Schema: which kinds of facts connect which kinds of entities", fontsize=14.5, fontfamily=SERIF, fontweight="bold", va="top")
    fig.text(0.01, 0.945, "ribbon width = number of facts   ·   not drawn: " + extra, fontsize=7.4, fontfamily=MONO, color=INK_FAINT, va="top")
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


# ---------------------------------------------------------------- drugs as an arc diagram
def draw_arcs(G, center="Đái tháo đường type 2", path=None, size=(13, 6.6)):
    atlas.style()
    drugs = [v for _, v, d in G.out_edges(center, data=True) if d["relation"] == "TREATED_BY"]
    cls = {d: next((c for c in G.successors(d) if G.nodes[c]["type"] == "DrugClass"), "") for d in drugs}
    drugs.sort(key=lambda d: (cls[d], -G[center][d]["support"]))
    effects = sorted({e for d in drugs for e in G.successors(d) if G[d][e]["relation"] == "HAS_SIDE_EFFECT"})
    nodes = [center] + drugs + effects
    x = {n: i + (0.6 if i > 0 else 0) + (0.6 if n in effects else 0) for i, n in enumerate(nodes)}
    fig, ax = plt.subplots(figsize=size)
    ax.axis("off"); ax.set_aspect("equal")
    top = (max(x.values()) / 2) * 0.62
    for d in drugs:
        w = abs(x[d] - x[center]) / 2
        ax.add_patch(matplotlib.patches.Arc(((x[d] + x[center]) / 2, 0), 2 * w, 1.2 * w, theta1=0, theta2=180,
                                            color=TYPE_COLORS["Drug"], lw=0.7 + 0.45 * math.log1p(G[center][d]["support"]), alpha=0.55))
    for d in drugs:
        for e in G.successors(d):
            if G[d][e]["relation"] != "HAS_SIDE_EFFECT":
                continue
            w = abs(x[e] - x[d]) / 2
            ax.add_patch(matplotlib.patches.Arc(((x[e] + x[d]) / 2, 0), 2 * w, 1.2 * w, theta1=0, theta2=180,
                                                color=ACCENT, lw=0.9 + 0.45 * math.log1p(G[d][e]["support"]), alpha=0.8))
    for n in nodes:
        ax.scatter([x[n]], [0], s=70, marker="D", color=TYPE_COLORS[G.nodes[n]["type"]], edgecolor=PAPER, lw=1, zorder=4)
        ax.text(x[n], -0.5, short(n, 24), rotation=90, ha="center", va="top", fontsize=8, color=INK)
    for i, c in enumerate(dict.fromkeys(cls[d] for d in drugs)):      # class brackets under the drug names
        xs = [x[d] for d in drugs if cls[d] == c]
        ax.plot([min(xs) - 0.3, max(xs) + 0.3], [-5.0, -5.0], color=TYPE_COLORS["DrugClass"], lw=3, solid_capstyle="butt")
        ax.text((min(xs) + max(xs)) / 2, -5.4 - 0.9 * (i % 2), short(c, 20), ha="center", va="top", fontsize=7.2, fontfamily=MONO,
                color=TYPE_COLORS["DrugClass"])
    ax.set_xlim(-1, max(x.values()) + 1); ax.set_ylim(-8, top + 2)
    ax.text(-0.9, top + 1.7, "━ treats type 2", fontsize=8, fontfamily=MONO, color=TYPE_COLORS["Drug"], va="top")
    ax.text(5.0, top + 1.7, "━ has side effect", fontsize=8, fontfamily=MONO, color=ACCENT, va="top")
    fig.suptitle("Type 2 treatment as an arc diagram", x=0.01, ha="left", fontfamily=SERIF, fontsize=14.5, fontweight="bold")
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


# ---------------------------------------------------------------- the teaching graph
def draw_toy(path=None, size=(11.5, 5.6)):
    atlas.style()
    fig, ax = plt.subplots(figsize=size)
    ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6.9)
    nodes = {"Đái tháo đường type 2": (1.9, 3, "DiabetesType"), "Khát nhiều": (6.2, 5.2, "Symptom"), "Tiểu nhiều": (6.2, 4.2, "Symptom"),
             "Thừa cân, béo phì": (6.2, 3.2, "RiskFactor"), "Bệnh thận đái tháo đường": (6.2, 2.0, "Complication"),
             "Metformin": (6.2, 0.8, "Drug"), "Thận": (10.4, 2.0, "Organ"), "Biguanide": (10.4, 0.8, "DrugClass")}
    edges = [("Đái tháo đường type 2", "Khát nhiều", "HAS_SYMPTOM"), ("Đái tháo đường type 2", "Tiểu nhiều", "HAS_SYMPTOM"),
             ("Đái tháo đường type 2", "Thừa cân, béo phì", "HAS_RISK_FACTOR"), ("Đái tháo đường type 2", "Bệnh thận đái tháo đường", "HAS_COMPLICATION"),
             ("Đái tháo đường type 2", "Metformin", "TREATED_BY"), ("Bệnh thận đái tháo đường", "Thận", "AFFECTS_ORGAN"),
             ("Metformin", "Biguanide", "BELONGS_TO_CLASS")]
    hot = {("Đái tháo đường type 2", "Bệnh thận đái tháo đường"), ("Bệnh thận đái tháo đường", "Thận")}
    w, h = 2.9, 0.62
    for s, o, r in edges:
        (x0, y0, _), (x1, y1, _) = nodes[s], nodes[o]
        on = (s, o) in hot
        ax.add_patch(FancyArrowPatch((x0 + w / 2, y0), (x1 - w / 2, y1), connectionstyle="arc3,rad=0.0", arrowstyle="-|>",
                                     mutation_scale=13, color=ACCENT if on else INK_FAINT, lw=2.4 if on else 1.1, zorder=1))
        tx = x0 + w / 2 + 0.62 * ((x1 - w / 2) - (x0 + w / 2)); ty = y0 + 0.62 * (y1 - y0)
        ax.text(tx, ty, r, fontsize=6.8, fontfamily=MONO, ha="center", va="bottom",
                color=ACCENT if on else INK_SOFT, rotation=0, bbox=dict(boxstyle="square,pad=0.1", fc=PAPER, ec="none"), zorder=2)
    for n, (x, y, t) in nodes.items():
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=PAPER, ec=TYPE_COLORS[t], lw=1.6, zorder=3))
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), 0.14, h, boxstyle="square,pad=0", fc=TYPE_COLORS[t], ec="none", zorder=4))
        ax.text(x + 0.05, y, n, ha="center", va="center", fontsize=8.6, fontweight="bold", zorder=5)
    ax.text(0.1, 6.85, "Seven facts, drawn left to right", fontfamily=SERIF, fontsize=14.5, fontweight="bold", va="top")
    ax.text(0.1, 6.42, "red path = the two-hop answer to “which organ does type 2 damage?”", fontfamily=MONO, fontsize=7.8, color=INK_FAINT, va="top")
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


# ---------------------------------------------------------------- small chart kinds
def bubble_matrix(pivot, title, sub=None, path=None, scale=950, color=ACCENT):
    atlas.style()
    rows, cols = list(pivot.index), list(pivot.columns)
    fig, ax = plt.subplots(figsize=(1.35 * len(cols) + 3.2, 0.42 * len(rows) + 2.4))
    ax.grid(False)
    vmax = float(pivot.values.max()) or 1
    for i, r in enumerate(rows):
        ax.axhline(i, color=RULE, lw=0.7, ls=(0, (1, 3)), zorder=0)
        for j, c in enumerate(cols):
            v = pivot.iloc[i, j]
            if v:
                ax.scatter(j, i, s=scale * (v / vmax) + 40, color=color, alpha=0.82, edgecolor=PAPER, lw=1, zorder=3)
                ax.text(j, i, int(v), ha="center", va="center", fontsize=7.2, color="white" if v / vmax > 0.12 else INK, fontweight="bold", zorder=4)
    ax.set_xticks(range(len(cols)), cols, fontsize=8.5, color=INK_SOFT)
    ax.set_yticks(range(len(rows)), rows, fontsize=8.5, color=INK)
    ax.invert_yaxis(); ax.tick_params(length=0)
    ax.set_xlim(-0.6, len(cols) - 0.4); ax.set_ylim(len(rows) - 0.4, -0.6)
    for s in ax.spines.values():
        s.set_visible(False)
    atlas.title(ax, title, sub)
    fig.tight_layout()
    if path:
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return fig


def lollipop(ax, labels, values, colors=None, fmt="{:.0f}", marker="D", head=60):
    y = np.arange(len(labels))
    colors = colors or [ACCENT] * len(labels)
    ax.hlines(y, 0, values, color=colors, lw=1.6, alpha=0.75)
    ax.scatter(values, y, s=head, marker=marker, color=colors, edgecolor=PAPER, lw=1, zorder=3)
    for yi, v in zip(y, values):
        ax.text(v + max(values) * 0.025, yi, fmt.format(v), va="center", fontsize=8, fontfamily=MONO, color=INK_SOFT)
    ax.set_yticks(y, labels); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0, labelsize=8.5, labelcolor=INK)
    ax.set_xlim(0, max(values) * 1.14)


def unit_chart(ax, counts, colors, per_row=None):
    """one diamond per item, one row per category"""
    per_row = per_row or max(counts.values())
    for i, (name, n) in enumerate(counts.items()):
        ax.scatter(np.arange(n), [i] * n, s=62, marker="D", color=colors[name], edgecolor=PAPER, lw=0.8)
        ax.text(-1.2, i, name, ha="right", va="center", fontsize=8.5, color=INK)
        ax.text(n + 0.4, i, n, ha="left", va="center", fontsize=8, fontfamily=MONO, color=INK_SOFT)
    ax.set_xlim(-1.4, per_row + 2.5); ax.set_ylim(len(counts) - 0.4, -0.6)
    ax.axis("off")


def ecdf(ax, values, color=ACCENT, log=False, marks=(0.25, 0.5, 0.9), unit=""):
    v = np.sort(np.asarray(values))
    y = np.arange(1, len(v) + 1) / len(v)
    ax.step(v, y, where="post", color=color, lw=2)
    ax.fill_between(v, y, step="post", color=color, alpha=0.10)
    for q in marks:
        x = float(np.quantile(v, q))
        ax.plot([x, x], [0, q], color=INK_FAINT, lw=0.8, ls=(0, (2, 2)))
        ax.scatter([x], [q], s=26, marker="D", color=INK, zorder=4)
        ax.annotate(f"{int(q * 100)}% ≤ {x:,.0f}{unit}", (x, q), textcoords="offset points", xytext=(6, -11), fontsize=7.4,
                    fontfamily=MONO, color=INK_SOFT)
    if log:
        ax.set_xscale("log")
    ax.set_ylim(0, 1.02); ax.set_yticks([0, .25, .5, .75, 1], ["0", "25%", "50%", "75%", "100%"])


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    G = build_graph()
    print(f"graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    draw_ring(G, FIG / "ring.png")
    draw_ego(G, "Đái tháo đường type 2", FIG / "ego_type2.png")
    print(f"saved figures to {FIG}")


if __name__ == "__main__":
    main()
