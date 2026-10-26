// Diabetes KG — example queries (paste into Neo4j Browser at http://localhost:7474)

// 0. Schema overview
CALL db.schema.visualization();

// 1. Symptoms of type 1 vs type 2: shared and unique
MATCH (t:DiabetesType)-[:HAS_SYMPTOM]->(s:Symptom)
WHERE t.name IN ['Đái tháo đường type 1', 'Đái tháo đường type 2']
WITH s, collect(t.name) AS types
RETURN s.name AS symptom,
       CASE size(types) WHEN 2 THEN 'both' ELSE types[0] END AS found_in
ORDER BY found_in, symptom;

// 2. Most frequently reported complications of diabetes (by number of supporting articles)
MATCH (:DiabetesType {name: 'Đái tháo đường'})-[r:HAS_COMPLICATION]->(c:Complication)
OPTIONAL MATCH (c)-[:AFFECTS_ORGAN]->(o:Organ)
RETURN c.name AS complication, o.name AS organ, r.support AS articles
ORDER BY articles DESC LIMIT 10;

// 3. Diagnostic tests and thresholds
MATCH (:DiabetesType)-[:DIAGNOSED_BY]->(t:Test)
RETURN DISTINCT t.name AS test, t.threshold AS threshold
ORDER BY threshold IS NULL, test;

// 4. Drugs by class, with side effects reported in the articles
MATCH (d:Drug)-[:BELONGS_TO_CLASS]->(c:DrugClass)
OPTIONAL MATCH (d)-[se:HAS_SIDE_EFFECT]->(e)
RETURN c.name AS class, d.name AS drug, collect(e.name) AS side_effects
ORDER BY class, drug;

// 5. Symptom checker: rank diabetes types by matching symptoms
WITH ['Khát nhiều', 'Tiểu nhiều', 'Sụt cân', 'Nhìn mờ'] AS input
MATCH (t:DiabetesType)-[r:HAS_SYMPTOM]->(s:Symptom)
WHERE s.name IN input
RETURN t.name AS type, count(s) AS matched, collect(s.name) AS symptoms, sum(r.support) AS evidence
ORDER BY matched DESC, evidence DESC;

// 6. Path: risk factor -> diabetes type -> complication -> organ
MATCH p = (rf:RiskFactor {name: 'Thừa cân, béo phì'})<-[:HAS_RISK_FACTOR]-(t:DiabetesType)
          -[:HAS_COMPLICATION]->(c:Complication)-[:AFFECTS_ORGAN]->(o:Organ {name: 'Thận'})
RETURN p;

// 7. Diet: recommended vs avoided foods for gestational diabetes
MATCH (:DiabetesType {name: 'Đái tháo đường thai kỳ'})-[r:RECOMMENDS_FOOD|AVOIDS_FOOD]->(f:Food)
RETURN type(r) AS advice, f.name AS food, r.support AS articles
ORDER BY advice, articles DESC;

// 8. Most central entities (most articles mention them)
MATCH (a:Article)-[:MENTIONS]->(e:Entity)
RETURN labels(e)[1] AS label, e.name AS entity, count(a) AS articles
ORDER BY articles DESC LIMIT 15;

// 9. Evidence: which articles support "type 2 has complication kidney disease"
MATCH (:DiabetesType {name: 'Đái tháo đường type 2'})-[r:HAS_COMPLICATION]->(:Complication {name: 'Bệnh thận đái tháo đường'})
UNWIND r.example_urls AS url
MATCH (a:Article {url: url})
RETURN a.title, a.url;

// 10. Co-occurring complications (mentioned in the same article)
MATCH (a:Article)-[:MENTIONS]->(c1:Complication), (a)-[:MENTIONS]->(c2:Complication)
WHERE c1.name < c2.name
RETURN c1.name, c2.name, count(a) AS together
ORDER BY together DESC LIMIT 10;

// 11. Whole knowledge graph without articles
MATCH (h:Entity)-[r]->(t:Entity) RETURN h, r, t;

// 12. One-hop query (lecture Exercise 1): everything directly connected to Metformin
MATCH (e:Entity {name: 'Metformin'})-[r]-(n:Entity)
RETURN e.name, type(r) AS relation, n.name AS neighbour, labels(n)[1] AS type;

// 13. Two-hop query (lecture Exercise 1): which organs can type 2 diabetes damage?
//     Đái tháo đường type 2 -HAS_COMPLICATION-> Complication -AFFECTS_ORGAN-> Organ
MATCH (t:DiabetesType {name: 'Đái tháo đường type 2'})-[:HAS_COMPLICATION]->(c)-[:AFFECTS_ORGAN]->(o:Organ)
RETURN o.name AS organ, collect(c.name) AS via_complications
ORDER BY size(via_complications) DESC;

// 14. Two-hop query: drug classes used for gestational diabetes
MATCH (:DiabetesType {name: 'Đái tháo đường thai kỳ'})-[:TREATED_BY]->(d:Drug)-[:BELONGS_TO_CLASS]->(c:DrugClass)
RETURN c.name AS class, collect(d.name) AS drugs;
