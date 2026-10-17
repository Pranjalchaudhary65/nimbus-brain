from db import get_graph
from seed import TEAMS, PEOPLE, PROJECTS, DEPENDS_ON, TOPICS, DOCS, DECISIONS

g = get_graph()
try:
    g.delete()          # start clean so this script can be re-run any time
except Exception:
    pass
g = get_graph()

def run(q, params=None):
    return g.query(q, params or {})

def link(rows, a_label, rel, b_label):
    run(f"UNWIND $rows AS r MATCH (a:{a_label} {{id:r.a}}), (b:{b_label} {{id:r.b}}) "
        f"MERGE (a)-[:{rel}]->(b)", {"rows": rows})

# indexes make lookups by id fast
for label in ["Team", "Person", "Project", "Document", "Decision", "Topic"]:
    try:
        run(f"CREATE INDEX FOR (n:{label}) ON (n.id)")
    except Exception:
        pass

# nodes
run("UNWIND $rows AS r MERGE (n:Team {id:r.id}) SET n.name=r.name", {"rows": TEAMS})
run("UNWIND $rows AS r MERGE (n:Person {id:r.id}) SET n.name=r.name, n.role=r.role", {"rows": PEOPLE})
run("UNWIND $rows AS r MERGE (n:Project {id:r.id}) SET n.name=r.name", {"rows": PROJECTS})
run("UNWIND $rows AS r MERGE (n:Topic {id:r.id}) SET n.name=r.name", {"rows": TOPICS})
run("UNWIND $rows AS r MERGE (n:Document {id:r.id}) SET n.title=r.title, n.date=r.date, n.text=r.text", {"rows": DOCS})
run("UNWIND $rows AS r MERGE (n:Decision {id:r.id}) SET n.title=r.title, n.date=r.date, n.status=r.status", {"rows": DECISIONS})

# relationships
link([{"a": p["id"], "b": p["team"]} for p in PEOPLE], "Person", "MEMBER_OF", "Team")
link([{"a": j["owner"], "b": j["id"]} for j in PROJECTS], "Person", "OWNS", "Project")
link([{"a": a, "b": b} for a, b in DEPENDS_ON], "Project", "DEPENDS_ON", "Project")
link([{"a": d["author"], "b": d["id"]} for d in DOCS], "Person", "AUTHORED", "Document")
link([{"a": d["id"], "b": t} for d in DOCS for t in d["topics"]], "Document", "ABOUT", "Topic")
link([{"a": d["id"], "b": j} for d in DOCS for j in d["projects"]], "Document", "MENTIONS", "Project")
link([{"a": d["by"], "b": d["id"]} for d in DECISIONS], "Person", "DECIDED", "Decision")
link([{"a": d["id"], "b": d["project"]} for d in DECISIONS], "Decision", "ABOUT", "Project")
link([{"a": d["id"], "b": doc} for d in DECISIONS for doc in d["based_on"]], "Decision", "BASED_ON", "Document")
link([{"a": d["id"], "b": d["supersedes"]} for d in DECISIONS if d["supersedes"]], "Decision", "SUPERSEDES", "Decision")

print("Nodes:", run("MATCH (n) RETURN count(n)").result_set[0][0])
print("Edges:", run("MATCH ()-[r]->() RETURN count(r)").result_set[0][0])