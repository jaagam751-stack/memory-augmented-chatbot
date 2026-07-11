
import re
from typing import Dict, List

from neo4j import GraphDatabase

from app.utils.config import settings


def _safe_relationship_type(value: str) -> str:
    """Neo4j relationship types must be uppercase and simple."""
    cleaned = re.sub(r"[^A-Z0-9_]+", "_", value.upper()).strip("_")
    return cleaned or "RELATED_TO"


class Neo4jGraphClient:
    """Beginner-friendly Neo4j helper class."""

    def __init__(self) -> None:
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )
            self.driver.verify_connectivity()
            self.ensure_constraints()
        except Exception:
            # The app can still run without Neo4j, but graph status will show unavailable.
            self.driver = None

    def is_available(self) -> bool:
        return self.driver is not None

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def ensure_constraints(self) -> None:
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")

    def store_graph(self, graph_data: Dict) -> Dict[str, int]:
        """Store entities and relationships returned by the extractor."""
        if not self.driver:
            return {"entities": 0, "relationships": 0}

        entities = graph_data.get("entities", [])
        relationships = graph_data.get("relationships", [])

        with self.driver.session() as session:
            for entity in entities:
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type
                    """,
                    name=entity.get("name"),
                    type=entity.get("type", "Other"),
                )

            for rel in relationships:
                rel_type = _safe_relationship_type(rel.get("relationship", "RELATED_TO"))
                cypher = f"""
                    MERGE (a:Entity {{name: $source}})
                    MERGE (b:Entity {{name: $target}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r.label = $label
                """
                session.run(
                    cypher,
                    source=rel.get("source"),
                    target=rel.get("target"),
                    label=rel_type,
                )

        return {"entities": len(entities), "relationships": len(relationships)}

    def search_context(self, query: str, limit: int = 8) -> str:
        """Retrieve graph facts whose entity names appear similar to the query."""
        if not self.driver:
            return "Neo4j is not connected, so no graph context is available."

        keywords = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9]{2,}", query)[:8]]
        if not keywords:
            return "No graph keywords found in the question."

        cypher = """
        MATCH (a:Entity)-[r]->(b:Entity)
        WHERE any(word IN $keywords WHERE toLower(a.name) CONTAINS word OR toLower(b.name) CONTAINS word)
        RETURN a.name AS source, type(r) AS relationship, b.name AS target
        LIMIT $limit
        """
        with self.driver.session() as session:
            records = session.run(cypher, keywords=keywords, limit=limit)
            facts: List[str] = [f"{r['source']} -[{r['relationship']}]-> {r['target']}" for r in records]

        return "\n".join(facts) if facts else "No matching graph facts found."

    def status(self) -> Dict[str, object]:
        """Return simple KG status for API and Streamlit."""
        if not self.driver:
            return {"connected": False, "entities": 0, "relationships": 0}
        with self.driver.session() as session:
            entities = session.run("MATCH (e:Entity) RETURN count(e) AS count").single()["count"]
            relationships = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
        return {"connected": True, "entities": entities, "relationships": relationships}
