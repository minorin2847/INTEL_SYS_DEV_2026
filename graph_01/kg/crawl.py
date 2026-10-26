"""Crawl diabetes-related pages from vinmec.com into dataset/raw/.

Pipeline:
  1. sitemap.xml -> all Vietnamese post/disease URLs
  2. keep URLs whose slug contains a diabetes keyword
  3. fetch each page (1 req/s), parse title, date, sections, paragraphs, bullets
  4. keep the page only if the text is really about diabetes (relevance score)
  5. write one JSON per page + an index CSV

Usage:
  python kg/crawl.py               # full crawl (resumable)
  python kg/crawl.py --limit 20    # quick test
"""
import argparse
import csv
import json
import re
import time
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vinmec.com"
SITEMAP = f"{BASE}/sitemap.xml"
HEADERS = {"User-Agent": "Mozilla/5.0 (student research crawler; B23DCDT285 knowledge-graph assignment)"}
DELAY = 1.0

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "dataset" / "raw"
PAGES_DIR = RAW_DIR / "pages"

# Slug keywords (no diacritics). Strong ones are diabetes by themselves,
# weak ones (insulin, đường huyết, ...) need the text check in step 4.
STRONG_SLUG = ["tieu-duong", "thao-duong", "dai-duong"]
WEAK_SLUG = ["insulin", "metformin", "hba1c", "duong-huyet", "glucose", "sglt2", "dpp-4",
             "sulfonylure", "tien-tieu-duong", "khang-insulin", "ceton"]
EXCLUDE_SLUG = ["thao-nhat"]  # đái tháo nhạt (diabetes insipidus) is a different disease

# Text terms used for the relevance score (lowercase, with diacritics).
CORE_TERMS = ["tiểu đường", "đái tháo đường", "đtđ"]
RELATED_TERMS = ["đường huyết", "insulin", "hba1c", "metformin", "glucose", "tuyến tụy",
                 "biến chứng", "kháng insulin", "hạ đường huyết", "tăng đường huyết"]

# Text that marks the end of the article body (ads, booking, related links).
CUT_MARKERS = ["Để đặt lịch khám", "Xem thêm:", "XEM THÊM:", "Bài viết liên quan",
               "Tải và đặt lịch khám", "Quý khách có thể trực tiếp đến"]


def slug_text(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def get(session, url, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(2 * (i + 1))
    return None


def collect_urls(session):
    xml = get(session, SITEMAP)
    maps = re.findall(r"<loc>([^<]+)</loc>", xml)
    maps = [m for m in maps if re.search(r"/(posts|diseases)-vi-\d+\.xml$", m)]
    urls = []
    for m in maps:
        urls += re.findall(r"<loc>([^<]+)</loc>", get(session, m) or "")
        time.sleep(0.3)
    keep = []
    for u in dict.fromkeys(urls):
        slug = u.rstrip("/").rsplit("/", 1)[-1]
        if any(x in slug for x in EXCLUDE_SLUG):
            continue
        if any(k in slug for k in STRONG_SLUG):
            keep.append((u, "strong"))
        elif any(k in slug for k in WEAK_SLUG):
            keep.append((u, "weak"))
    return keep


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def cut_boilerplate(blocks):
    out = []
    for b in blocks:
        if any(b["text"].startswith(m) for m in CUT_MARKERS):
            break
        out.append(b)
    return out


def parse_blocks(container):
    """Flatten a content container into ordered blocks: heading / paragraph / list."""
    blocks = []
    for el in container.find_all(["h2", "h3", "h4", "p", "ul", "ol"]):
        if el.find_parent(["ul", "ol"]) and el.name in ("p", "ul", "ol"):
            continue  # nested inside a list already captured
        if el.name in ("ul", "ol"):
            items = [clean(li.get_text(" ")) for li in el.find_all("li", recursive=False)]
            items = [i for i in items if i]
            if items:
                blocks.append({"type": "list", "text": " | ".join(items), "items": items})
        else:
            t = clean(el.get_text(" "))
            if t:
                blocks.append({"type": "heading" if el.name[0] == "h" else "paragraph",
                               "level": el.name, "text": t})
    return cut_boilerplate(blocks)


def group_sections(blocks, first_title):
    sections, cur = [], {"heading": first_title, "paragraphs": [], "bullets": []}
    for b in blocks:
        if b["type"] == "heading" and b["level"] in ("h2", "h3"):
            if cur["paragraphs"] or cur["bullets"]:
                sections.append(cur)
            cur = {"heading": b["text"], "paragraphs": [], "bullets": []}
        elif b["type"] == "list":
            cur["bullets"] += b["items"]
        else:
            cur["paragraphs"].append(b["text"])
    if cur["paragraphs"] or cur["bullets"]:
        sections.append(cur)
    return sections


def parse_article(html, url):
    s = BeautifulSoup(html, "html.parser")
    meta = {}
    for ld in s.find_all("script", type="application/ld+json"):
        try:
            graph = json.loads(ld.text).get("@graph", [])
        except json.JSONDecodeError:
            continue
        for g in graph:
            if g.get("@type") in ("NewsArticle", "Article", "MedicalWebPage"):
                meta = g
    h1 = s.find("h1")
    title = clean(meta.get("headline") or (h1.get_text() if h1 else s.title.text.split("|")[0]))
    entry = s.select_one(".entry")
    if entry is None:
        return None
    author = meta.get("author") or {}
    return {
        "url": url, "page_type": "article", "title": title,
        "description": clean(meta.get("description", "")),
        "date_published": meta.get("datePublished"),
        "author": author.get("name") if isinstance(author, dict) else None,
        "sections": group_sections(parse_blocks(entry), "Mở đầu"),
    }


def parse_disease(html, url):
    s = BeautifulSoup(html, "html.parser")
    title = clean(s.title.text.split("|")[0]) if s.title else url
    sections = []
    for item in s.select(".item_detial_sick"):
        h = item.select_one(".title_detail_sick") or item.find("h2")
        body = item.select_one(".body") or item
        heading = clean(h.get_text()) if h else ""
        for sec in group_sections(parse_blocks(body), heading):
            sections.append(sec)
    if not sections:
        return None
    return {"url": url, "page_type": "disease", "title": title, "description": "",
            "date_published": None, "author": "Vinmec", "sections": sections}


def full_text(doc):
    parts = [doc["title"], doc["description"]]
    for sec in doc["sections"]:
        parts += [sec["heading"], *sec["paragraphs"], *sec["bullets"]]
    return " ".join(p for p in parts if p)


def relevance(doc):
    text = full_text(doc).lower()
    head = (doc["title"] + " " + doc["description"]).lower()
    core = sum(text.count(t) for t in CORE_TERMS)
    related = sum(text.count(t) for t in RELATED_TERMS)
    in_head = any(t in head for t in CORE_TERMS)
    return core, related, in_head


def is_relevant(doc, strength):
    core, related, in_head = relevance(doc)
    if doc["page_type"] == "disease":
        return True
    if in_head and core >= 2:
        return True
    # weak-slug pages (e.g. insulin, đường huyết) must talk about diabetes a lot
    return strength == "strong" and core >= 3 or core >= 5 and related >= 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="max pages to fetch (0 = all)")
    args = ap.parse_args()

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    print("1) Reading sitemap ...")
    candidates = collect_urls(session)
    candidates.sort(key=lambda x: ("/benh/" not in x[0], x[1] != "strong"))
    print(f"   {len(candidates)} candidate URLs "
          f"({sum(1 for _, s in candidates if s == 'strong')} strong slug)")
    if args.limit:
        candidates = candidates[:args.limit]

    index, seen_titles = [], set()
    for i, (url, strength) in enumerate(candidates, 1):
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        out = PAGES_DIR / f"{slug[:150]}.json"
        if out.exists():  # resume
            doc = json.loads(out.read_text())
        else:
            html = get(session, url)
            time.sleep(DELAY)
            if not html:
                print(f"   [{i}/{len(candidates)}] fetch failed {url}")
                continue
            doc = parse_disease(html, url) if "/benh/" in url else parse_article(html, url)
            if doc is None:
                continue
        key = slug_text(doc["title"])
        if key in seen_titles:  # same article published under two slugs
            continue
        core, related, _ = relevance(doc)
        keep = is_relevant(doc, strength)
        index.append({"slug": slug, "url": url, "page_type": doc["page_type"], "title": doc["title"],
                      "date_published": doc["date_published"], "n_sections": len(doc["sections"]),
                      "n_words": len(full_text(doc).split()), "core_mentions": core,
                      "related_mentions": related, "slug_match": strength, "relevant": keep})
        if keep:
            seen_titles.add(key)
            out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
        elif out.exists():
            out.unlink()
        if i % 25 == 0:
            print(f"   [{i}/{len(candidates)}] kept {sum(r['relevant'] for r in index)}")

    with open(RAW_DIR / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(index[0].keys()))
        w.writeheader()
        w.writerows(index)
    kept = [r for r in index if r["relevant"]]
    print(f"Done: {len(kept)} relevant pages saved to {PAGES_DIR} "
          f"({len(index) - len(kept)} rejected), index at {RAW_DIR / 'index.csv'}")


if __name__ == "__main__":
    main()
