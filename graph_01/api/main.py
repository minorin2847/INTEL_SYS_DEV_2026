"""FastAPI service over the Neo4j diabetes Knowledge Graph.

    browser (web/) -> /api/* -> this service -> Neo4j (read-only Cypher)

Run:  uvicorn api.main:app --reload --port 8000    (from the graph_01/ directory)
Docs: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import ServiceUnavailable

from . import config, db
from .schema import Article, EntityDetail, EntitySummary, Fact, Path, Stats, SymptomMatch, SymptomQuery

TYPE = "[l IN labels({v}) WHERE l <> 'Entity'][0]"


@asynccontextmanager
async def lifespan(_app):
    yield
    db.close()


app = FastAPI(title="Diabetes Knowledge Graph API", version="1.0.0", lifespan=lifespan,
              description="Read-only access to the diabetes KG extracted from Vinmec articles.")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["GET", "POST"],
                   allow_headers=["*"])


@app.exception_handler(ServiceUnavailable)
async def _neo4j_down(_request, _exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=503, content={"detail": "The Neo4j database is not reachable."})


@app.get("/health")
def health():
    db.read("RETURN 1 AS ok")
    return {"status": "ok"}


@app.get("/stats", response_model=Stats)
def stats():
    nodes = db.read(f"MATCH (n:Entity) RETURN {TYPE.format(v='n')} AS name, count(*) AS n ORDER BY n DESC")
    rels = db.read("MATCH (:Entity)-[r]->(:Entity) RETURN type(r) AS name, count(*) AS n ORDER BY n DESC")
    articles = db.read("MATCH (a:Article) RETURN count(a) AS n")[0]["n"]
    return {"nodes": nodes, "relations": rels, "articles": articles, "facts": sum(r["n"] for r in rels)}


@app.get("/entities", response_model=list[EntitySummary])
def entities(q: str = "", type: str | None = None, limit: int = Query(20, ge=1, le=200)):
    return db.read(f"""
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($q) AND ($type IS NULL OR $type IN labels(e))
        RETURN e.name AS name, {TYPE.format(v='e')} AS type, COUNT {{ (e)--(:Entity) }} AS degree
        ORDER BY CASE WHEN toLower(e.name) STARTS WITH toLower($q) THEN 0 ELSE 1 END, degree DESC
        LIMIT $limit""", q=q.strip(), type=type, limit=limit)


@app.get("/entities/{name}", response_model=EntityDetail)
def entity(name: str, min_support: int = Query(0, ge=0)):
    rows = db.read(f"""
        MATCH (e:Entity {{name: $name}})
        RETURN e.name AS name, {TYPE.format(v='e')} AS type, e.threshold AS threshold,
               COUNT {{ (:Article)-[:MENTIONS|ABOUT]->(e) }} AS mentioned_in""", name=name)
    if not rows:
        raise HTTPException(404, f"No entity named '{name}'.")
    facts = db.read(f"""
        MATCH (e:Entity {{name: $name}})-[r]-(n:Entity)
        WHERE r.source = 'curated' OR r.support >= $min_support
        WITH startNode(r) AS s, r, endNode(r) AS o
        RETURN s.name AS subject, {TYPE.format(v='s')} AS subject_type, type(r) AS relation,
               o.name AS object, {TYPE.format(v='o')} AS object_type,
               coalesce(r.support, 0) AS support, r.source AS source
        ORDER BY support DESC LIMIT $cap""", name=name, min_support=min_support, cap=config.MAX_FACTS)
    return {**rows[0], "facts": facts}


@app.get("/evidence", response_model=list[Article])
def evidence(subject: str, relation: str, object: str):
    return db.read("""
        MATCH (:Entity {name: $subject})-[r]->(:Entity {name: $object})
        WHERE type(r) = $relation
        UNWIND coalesce(r.example_urls, []) AS url
        MATCH (a:Article {url: url})
        RETURN a.title AS title, a.url AS url, a.date AS date""", subject=subject, relation=relation, object=object)


@app.get("/entities/{name}/articles", response_model=list[Article])
def entity_articles(name: str, limit: int = Query(10, ge=1, le=50)):
    return db.read("""
        MATCH (a:Article)-[:MENTIONS|ABOUT]->(:Entity {name: $name})
        RETURN a.title AS title, a.url AS url, a.date AS date
        ORDER BY a.date DESC LIMIT $limit""", name=name, limit=limit)


@app.post("/symptom-check", response_model=list[SymptomMatch])
def symptom_check(body: SymptomQuery):
    return db.read("""
        MATCH (t:DiabetesType)-[r:HAS_SYMPTOM]->(s:Symptom)
        WHERE s.name IN $symptoms AND r.support >= $min_support
        RETURN t.name AS type, collect(s.name) AS matched, sum(r.support) AS evidence
        ORDER BY size(matched) DESC, evidence DESC""", symptoms=body.symptoms, min_support=body.min_support)


@app.get("/paths", response_model=list[Path])
def paths(source: str, target: str, limit: int = Query(5, ge=1, le=20)):
    if source == target:
        raise HTTPException(422, "Choose two different entities.")
    rows = db.read(f"""
        MATCH (a:Entity {{name: $source}}), (b:Entity {{name: $target}})
        MATCH p = allShortestPaths((a)-[*..{config.MAX_HOPS}]-(b))
        WHERE all(n IN nodes(p) WHERE n:Entity)
        RETURN [n IN nodes(p) | {{name: n.name, type: {TYPE.format(v='n')}, degree: COUNT {{ (n)--(:Entity) }}}}] AS nodes,
               [i IN range(0, length(p) - 1) | type(relationships(p)[i])] AS relations,
               [i IN range(0, length(p) - 1) | startNode(relationships(p)[i]) = nodes(p)[i]] AS forward
        LIMIT $limit""", source=source, target=target, limit=limit)
    return rows
