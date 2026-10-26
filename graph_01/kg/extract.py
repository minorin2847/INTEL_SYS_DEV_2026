"""Extract (subject, relation, object) triples from dataset/raw/pages/*.json.

For every page:
  subject = the diabetes type in the title (type 1 / 2 / thai kỳ / tiền ĐTĐ), else "Đái tháo đường"
  for every section: heading keywords decide which entity labels are allowed,
  then vocabulary aliases are matched in the section's paragraphs and bullets.
A triple is kept if it is supported by >= MIN_SUPPORT pages (or by a disease page).
Drug side effects are taken from sentences that contain a drug + "tác dụng phụ"/"gây".

Output: dataset/processed/{entities,triples,mentions}.csv
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from vocab import (DISEASE_TERMS, FOOD_AVOID, OTHER_TOPIC, REDUCE_VERBS, STRICT_LABELS, COMPLICATION_ORGAN, DIABETES_TYPES, DRUG_CLASS, GENERAL,
                   RELATION_BY_LABEL, SECTION_RULES, THRESHOLDS, VOCAB)

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "dataset" / "raw" / "pages"
OUT = ROOT / "dataset" / "processed"
MIN_SUPPORT = 2
MIN_SUPPORT_SIDE_EFFECT = 3

PATTERNS = {name: re.compile(r"(?<!\w)(" + "|".join(map(re.escape, sorted(al, key=len, reverse=True))) + r")(?!\w)")
            for name, (_, al) in VOCAB.items()}
LABEL = {name: lab for name, (lab, _) in VOCAB.items()}


def subject_of(title):
    t = title.lower()
    for name, aliases in DIABETES_TYPES.items():
        if any(a in t for a in aliases):
            return name
    return GENERAL


def about_disease(heading):
    """Generic heading ("Triệu chứng", "Ai dễ bị?") or one that names diabetes, and no other topic."""
    h = re.sub(r"^[\d\.\s]+", "", heading.lower())
    if any(t in h for t in OTHER_TOPIC) or any(v + " nguy cơ" in h for v in REDUCE_VERBS):
        return False
    return any(t in h for t in DISEASE_TERMS) or len(h.split()) <= 5


def allowed_labels(heading):
    h = heading.lower()
    labels = set()
    for keys, labs in SECTION_RULES:
        if any(k in h for k in keys):
            labels |= labs
    if not about_disease(heading):
        labels -= STRICT_LABELS
    return labels


def matches(text, labels):
    t = text.lower()
    return [n for n, p in PATTERNS.items() if LABEL[n] in labels and p.search(t)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    support = defaultdict(set)      # (h, rel, t) -> set(url)
    mentions = defaultdict(set)     # url -> entities mentioned anywhere
    from_disease = set()
    articles = []

    for f in sorted(PAGES.glob("*.json")):
        doc = json.loads(f.read_text())
        url, subj = doc["url"], subject_of(doc["title"])
        articles.append((url, doc["title"], doc["page_type"], doc.get("date_published") or "", subj))
        for sec in doc["sections"]:
            labels = allowed_labels(sec["heading"])
            units = sec["paragraphs"] + sec["bullets"]
            for unit in units:
                mentions[url].update(matches(unit, set(LABEL.values())))
                for ent in matches(unit, labels):
                    lab = LABEL[ent]
                    if lab == "Food":
                        rel = "AVOIDS_FOOD" if ent in FOOD_AVOID else "RECOMMENDS_FOOD"
                    else:
                        rel = RELATION_BY_LABEL[lab]
                    key = (subj, rel, ent)
                    support[key].add(url)
                    if doc["page_type"] == "disease":
                        from_disease.add(key)
                # drug side effects: one sentence with a drug and a symptom/complication
                for sent in re.split(r"(?<=[\.;!?])\s+", unit):
                    s = sent.lower()
                    if not ("tác dụng phụ" in s or "tác dụng không mong muốn" in s or " gây " in s):
                        continue
                    if "thiếu" in s or "không đủ" in s:  # "thiếu insulin gây ..." is a cause, not a side effect
                        continue
                    drugs = matches(sent, {"Drug"})
                    effects = matches(sent, {"Symptom", "Complication"})
                    for d in drugs:
                        for e in effects:
                            support[(d, "HAS_SIDE_EFFECT", e)].add(url)

    triples = []
    for (h, rel, t), urls in support.items():
        need = MIN_SUPPORT_SIDE_EFFECT if rel == "HAS_SIDE_EFFECT" else MIN_SUPPORT
        if len(urls) >= need or (h, rel, t) in from_disease:
            triples.append((h, rel, t, len(urls), "vinmec", " ".join(sorted(urls)[:5])))
    # curated background knowledge
    for d, c in DRUG_CLASS.items():
        triples.append((d, "BELONGS_TO_CLASS", c, 0, "curated", ""))
    for c, o in COMPLICATION_ORGAN.items():
        triples.append((c, "AFFECTS_ORGAN", o, 0, "curated", ""))
    for ty in DIABETES_TYPES:
        triples.append((ty, "SUBTYPE_OF", GENERAL, 0, "curated", ""))

    entities = {GENERAL: "DiabetesType", **{t: "DiabetesType" for t in DIABETES_TYPES}}
    entities.update(LABEL)
    entities.update({c: "DrugClass" for c in DRUG_CLASS.values()})
    entities.update({o: "Organ" for o in COMPLICATION_ORGAN.values()})
    used = {x for tr in triples for x in (tr[0], tr[2])}

    with open(OUT / "entities.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "label", "threshold"])
        for n, lab in sorted(entities.items(), key=lambda x: (x[1], x[0])):
            if n in used:
                w.writerow([n, lab, THRESHOLDS.get(n, "")])
    with open(OUT / "triples.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subject", "relation", "object", "support", "source", "example_urls"])
        w.writerows(sorted(triples, key=lambda x: (x[1], x[0], -x[3])))
    with open(OUT / "articles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "title", "page_type", "date_published", "about"])
        w.writerows(articles)
    with open(OUT / "mentions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "entity"])
        for url, ents in mentions.items():
            for e in sorted(ents):
                w.writerow([url, e])

    by_rel = defaultdict(int)
    for tr in triples:
        by_rel[tr[1]] += 1
    print(f"{len(articles)} pages -> {len(used)} entities, {len(triples)} triples")
    for r, n in sorted(by_rel.items(), key=lambda x: -x[1]):
        print(f"  {r:18s} {n}")


if __name__ == "__main__":
    main()
