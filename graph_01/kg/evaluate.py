"""Sample extracted triples with their evidence sentence for manual checking.

  python kg/evaluate.py   -> evaluation/manual_audit.csv (fill in the `correct` column)
"""
import csv
import json
import random
import re
from pathlib import Path

from extract import LABEL, PATTERNS, allowed_labels

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 50, 42


def evidence(urls, subj_ent, obj):
    """First sentence mentioning the object, searched only in sections the extractor used."""
    pat = PATTERNS[obj] if obj in PATTERNS else PATTERNS.get(subj_ent)
    for url in urls:
        doc = json.loads((ROOT / "dataset" / "raw" / "pages" /
                          (url.rstrip("/").rsplit("/", 1)[-1][:150] + ".json")).read_text())
        for sec in doc["sections"]:
            labels = allowed_labels(sec["heading"])
            if subj_ent is None and LABEL[obj] not in labels:
                continue
            for unit in sec["paragraphs"] + sec["bullets"]:
                for sent in re.split(r"(?<=[\.;!?])\s+", unit):
                    if pat and pat.search(sent.lower()):
                        return url, doc["title"], sec["heading"], sent[:300]
    return urls[0], "", "", ""


def main():
    with open(ROOT / "dataset" / "processed" / "triples.csv", encoding="utf-8") as f:
        triples = [t for t in csv.DictReader(f) if t["source"] == "vinmec"]
    random.seed(SEED)
    sample = random.sample(triples, N)
    out = ROOT / "evaluation" / "manual_audit.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "subject", "relation", "object", "support", "article", "section", "evidence", "url",
                    "correct", "error_type"])
        for i, t in enumerate(sample, 1):
            subj_ent = t["subject"] if t["relation"] == "HAS_SIDE_EFFECT" else None
            url, title, sec, sent = evidence(t["example_urls"].split(), subj_ent, t["object"])
            w.writerow([i, t["subject"], t["relation"], t["object"], t["support"], title, sec, sent, url, "", ""])
    print(f"{N} of {len(triples)} extracted triples -> {out}")


if __name__ == "__main__":
    main()
