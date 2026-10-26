"""Graph retrieval over the Neo4j diabetes KG (lecture §5.1 / §15.1).

graph_facts(entity, hops) starts from one entity and follows explicit relationships
1 or 2 hops out, instead of returning the whole graph (lecture §23.4).

  python kg/retriever.py "Metformin"
  python kg/retriever.py "Đái tháo đường type 2" --hops 2
"""
import argparse
import os

from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "diabetes123"))

ONE_HOP = """
MATCH (e:Entity {name: $name})-[r]-(n:Entity)
RETURN startNode(r).name AS s, type(r) AS rel, endNode(r).name AS o, r.support AS support
ORDER BY support DESC
"""

# second hop only through entity-to-entity relations, never back to the start
TWO_HOP = """
MATCH (e:Entity {name: $name})-[r1]-(m:Entity)-[r2]-(n:Entity)
WHERE n <> e
RETURN startNode(r2).name AS s, type(r2) AS rel, endNode(r2).name AS o, r2.support AS support
ORDER BY support DESC
"""


def graph_facts(driver, entity, hops=1, limit=30):
    facts, seen = [], set()
    queries = [ONE_HOP] + ([TWO_HOP] if hops >= 2 else [])
    with driver.session() as s:
        for q in queries:
            for r in s.run(q, name=entity):
                key = (r["s"], r["rel"], r["o"])
                if key not in seen:
                    seen.add(key)
                    facts.append(f"{r['s']} {r['rel']} {r['o']}.")
    return facts[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("--hops", type=int, default=1, choices=[1, 2])
    args = ap.parse_args()
    driver = GraphDatabase.driver(URI, auth=AUTH)
    for f in graph_facts(driver, args.entity, args.hops):
        print(f)
    driver.close()


if __name__ == "__main__":
    main()
