# Graph 01: Diabetes Knowledge Graph from Vinmec with Neo4j

Build a Knowledge Graph about diabetes (đái tháo đường / tiểu đường): its types, symptoms, causes, risk factors, complications, tests, drugs, diet and lifestyle advice, from public Vinmec articles. Store it in Neo4j and query it with Cypher.

```
graph_01/
├── kg/            pipeline: crawl → extract → load, plus retrieval, drawing, evaluation and Cypher queries
├── dataset/       raw/ (crawled pages + index), processed/ (entities, triples, articles, mentions CSV)
├── evaluation/    manual check of 50 sampled facts
├── notebook/      01_diabetes_kg.ipynb: every step explained and run
├── api/, web/     FastAPI service + React explorer ("Glyco Atlas")
└── report/        Graph_01.tex / .pdf
```

| File | Role |
|---|---|
| `kg/crawl.py` | Vinmec sitemap → diabetes pages → `dataset/raw/` |
| `kg/vocab.py` | vocabulary, section rules, curated facts |
| `kg/extract.py` | pages → `dataset/processed/*.csv` |
| `kg/load.py` | CSV → Neo4j |
| `kg/retriever.py` | `graph_facts(entity, hops)` |
| `kg/visualize.py` | NetworkX/matplotlib figures (ring layout, arcs, lollipops) |
| `kg/evaluate.py` | random sample of facts for the manual check |
| `kg/queries.cypher` | example Cypher queries for Neo4j Browser |

## Run

Everything runs with **Docker Compose**:

```bash
# Build and start all services (Neo4j, FastAPI, React web)
docker compose up --build

# Load the dataset into Neo4j (first-time setup or reload)
docker compose run --rm load

# Optional: rebuild the processed CSVs or re-crawl the raw pages
docker compose run --rm load python kg/extract.py
docker compose run --rm load python kg/crawl.py

# Stop everything (add -v to drop volumes)
docker compose down
```

| Service | Address | Role |
|---|---|---|
| **Web Explorer** | http://localhost:5173 | React + Vite UI |
| **FastAPI** | http://localhost:8000 (docs at `/docs`) | KG API backend |
| **Neo4j Browser** | http://localhost:7474 (`neo4j` / `diabetes123`) | graph database and Cypher |

Open http://localhost:7474 and run queries from `kg/queries.cypher`.

## Dataset

| Path | Content | In git |
|---|---|---|
| `dataset/raw/pages/*.json` | 1,096 Vinmec diabetes pages, one per article: title, URL, date, sections (heading, paragraphs, bullets) | no (copyrighted text; rebuild with `python kg/crawl.py`) |
| `dataset/raw/index.csv` | every checked candidate page with its mention counts and whether it was kept | yes |
| `dataset/processed/entities.csv` | `name, label, threshold` | yes |
| `dataset/processed/triples.csv` | `subject, relation, object, support, source, example_urls` | yes |
| `dataset/processed/articles.csv` | `url, title, page_type, date_published, about` | yes |
| `dataset/processed/mentions.csv` | `url, entity`: every entity mentioned anywhere on a page | yes |

Source: public articles of https://www.vinmec.com (`/vie/bai-viet/`, `/vie/benh/`), collected through the sitemap at 1 request per second. `dataset/processed/` is rebuilt with `python kg/extract.py`.

## Graph

127 entities (DiabetesType, Symptom, RiskFactor, Complication, Test, Drug, DrugClass, Food, Lifestyle, Organ), 339 facts and 1,096 Article nodes. A fact extracted from text needs at least 2 supporting pages (3 for side effects), or must come from a Vinmec disease page; `support` on each relationship counts the pages. Facts with `source = "curated"` (drug class, affected organ, subtype) and the diagnostic thresholds are background knowledge, not extracted.

## Website

**Glyco Atlas**, a small explorer for the graph: search any entity, see its facts with the number of supporting articles and the source links, compare diabetes types, check symptoms, and find connections between two entities.

```
browser (web/, React + Vite) ──/api──▶ api/ (FastAPI) ──Cypher, read-only──▶ Neo4j
```

| Page | URL |
|---|---|
| Home: search, graph size, start points, legend of entries | `#/` |
| Entity: facts grouped by relation, evidence links, neighbourhood, articles | `#/entity/Metformin` |
| Diabetes types side by side | `#/types/Đái tháo đường type 2` |
| Symptom finder | `#/symptoms` |
| Trace a link (shortest chains between two entities) | `#/paths?from=…&to=…` |

## Evaluation

`evaluation/manual_audit.csv` holds 50 randomly sampled extracted facts, each checked against all its source articles: 48 of 50 are correct (precision 0.96, likely range 0.87–0.99). Details in `evaluation/README.md`.

## Report

`report/Graph_01.pdf`, built from `report/Graph_01.tex` with XeLaTeX.
