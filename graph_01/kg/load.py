"""Load dataset/processed/*.csv into Neo4j.

  docker run -d --name neo4j-diabetes -p 7474:7474 -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/diabetes123 -v "$PWD/neo4j_data:/data" neo4j:5
  python kg/load.py            # wipes the database and reloads

Graph:
  (:Entity:<Label> {name, threshold?})  -[:<RELATION> {support, source}]->  (:Entity)
  (:Article {url, title, page_type, date})  -[:MENTIONS]->  (:Entity)
  (:Article)  -[:ABOUT]->  (:DiabetesType)
"""
import csv
import os
import time
from collections import defaultdict
from pathlib import Path

from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed"
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "diabetes123"))
LABELS = ["DiabetesType", "Symptom", "RiskFactor", "Complication", "Test", "Drug",
          "DrugClass", "Food", "Lifestyle", "Organ"]


def rows(name):
    with open(DATA / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def batches(items, n=500):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def connect(retries=30):
    for _ in range(retries):
        try:
            driver = GraphDatabase.driver(URI, auth=AUTH)
            driver.verify_connectivity()
            return driver
        except Exception:
            time.sleep(2)
    raise SystemExit(f"Cannot connect to Neo4j at {URI}")


def main():
    driver = connect()
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")
        s.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
        s.run("CREATE CONSTRAINT article_url IF NOT EXISTS FOR (a:Article) REQUIRE a.url IS UNIQUE")

        ents = rows("entities.csv")
        for lab in LABELS:  # labels cannot be parameters in Cypher
            part = [e for e in ents if e["label"] == lab]
            s.run(f"UNWIND $rows AS r MERGE (e:Entity {{name: r.name}}) SET e:{lab}, "
                  "e.threshold = CASE r.threshold WHEN '' THEN null ELSE r.threshold END", rows=part)

        by_rel = defaultdict(list)
        for t in rows("triples.csv"):
            t["support"] = int(t["support"])
            t["example_urls"] = t["example_urls"].split()
            by_rel[t["relation"]].append(t)
        for rel, part in by_rel.items():
            s.run(f"UNWIND $rows AS r MATCH (h:Entity {{name: r.subject}}), (t:Entity {{name: r.object}}) "
                  f"MERGE (h)-[x:{rel}]->(t) SET x.support = r.support, x.source = r.source, "
                  "x.example_urls = r.example_urls", rows=part)

        arts = rows("articles.csv")
        for part in batches(arts):
            s.run("UNWIND $rows AS r MERGE (a:Article {url: r.url}) "
                  "SET a.title = r.title, a.page_type = r.page_type, a.date = r.date_published "
                  "WITH a, r MATCH (d:DiabetesType {name: r.about}) MERGE (a)-[:ABOUT]->(d)", rows=part)
        for part in batches(rows("mentions.csv"), 2000):
            s.run("UNWIND $rows AS r MATCH (a:Article {url: r.url}), (e:Entity {name: r.entity}) "
                  "MERGE (a)-[:MENTIONS]->(e)", rows=part)

        print("Nodes:")
        for r in s.run("MATCH (n) UNWIND labels(n) AS l WITH l WHERE l <> 'Entity' "
                       "RETURN l, count(*) AS n ORDER BY n DESC"):
            print(f"  {r['l']:14s} {r['n']}")
        print("Relationships:")
        for r in s.run("MATCH ()-[x]->() RETURN type(x) AS t, count(*) AS n ORDER BY n DESC"):
            print(f"  {r['t']:18s} {r['n']}")
    driver.close()


if __name__ == "__main__":
    main()
