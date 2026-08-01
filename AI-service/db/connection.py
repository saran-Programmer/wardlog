import os

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
)


def verify_connection() -> None:
    driver.verify_connectivity()


def close_driver() -> None:
    driver.close()
