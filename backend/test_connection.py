from db import get_graph

g = get_graph("test")
print(g.query("MATCH (p:Person)-[:OWNS]->(j:Project) RETURN p.name, j.name").result_set)