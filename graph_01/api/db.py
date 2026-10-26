"""Neo4j driver: one shared driver, read-only queries returning plain dicts."""
from neo4j import GraphDatabase, RoutingControl

from . import config

_driver = None


def driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
    return _driver


def read(query, **params):
    records, _, _ = driver().execute_query(query, params, routing_=RoutingControl.READ)
    return [r.data() for r in records]


def close():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
