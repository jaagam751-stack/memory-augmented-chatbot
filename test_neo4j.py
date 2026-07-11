from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
username = "username"
password = "your password"

driver = GraphDatabase.driver(uri, auth=(username, password))

with driver.session() as session:
    result = session.run("RETURN 'Neo4j Connected Successfully' AS message")
    print(result.single()["message"])

driver.close()
