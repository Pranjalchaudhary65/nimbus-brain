import json
from db import get_graph

g = get_graph()

def q(cypher, params=None):
    return g.query(cypher, params or {}).result_set

def trace_decision(decision_id):
    """WHY was a decision made? Follows SUPERSEDES and BASED_ON links."""
    rows = q("""
        MATCH p=(d:Decision {id:$id})-[:SUPERSEDES|BASED_ON*1..3]->(x)
        UNWIND relationships(p) AS r
        RETURN DISTINCT startNode(r).id, coalesce(startNode(r).title, startNode(r).name),
               type(r), endNode(r).id, coalesce(endNode(r).title, endNode(r).name)
    """, {"id": decision_id})
    return {"tool": "trace_decision",
            "path": [{"from_id": r[0], "from": r[1], "rel": r[2], "to_id": r[3], "to": r[4]} for r in rows]}

def impact_analysis(project_name):
    """WHAT BREAKS if this project changes? Follows DEPENDS_ON up to 3 hops."""
    hops = q("""
        MATCH p=(j:Project {name:$n})<-[:DEPENDS_ON*1..3]-(x:Project)
        RETURN x.name, min(length(p))
    """, {"n": project_name})
    edges = q("""
        MATCH p=(j:Project {name:$n})<-[:DEPENDS_ON*1..3]-(x:Project)
        UNWIND relationships(p) AS r
        RETURN DISTINCT startNode(r).name, endNode(r).name
    """, {"n": project_name})
    return {"tool": "impact_analysis",
            "affected": sorted([{"project": h[0], "hops": h[1]} for h in hops], key=lambda d: d["hops"]),
            "path": [{"from": e[0], "rel": "DEPENDS_ON", "to": e[1]} for e in edges]}

def find_owner(project_name):
    """WHO owns this project, and on which team?"""
    rows = q("""
        MATCH (p:Person)-[:OWNS]->(j:Project {name:$n})
        OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
        RETURN p.name, p.role, t.name
    """, {"n": project_name})
    return {"tool": "find_owner",
            "owners": [{"name": r[0], "role": r[1], "team": r[2]} for r in rows],
            "path": [{"from": r[0], "rel": "OWNS", "to": project_name} for r in rows]}
def who_knows(topic):
    """WHO knows most about a topic? Ranks people by documents they wrote about it."""
    rows = q("""
        MATCH (p:Person)-[:AUTHORED]->(d:Document)-[:ABOUT]->(t:Topic {name:$t})
        RETURN p.name, p.role, count(d) AS docs, collect(d.title)
        ORDER BY docs DESC
    """, {"t": topic})
    path = []
    for r in rows:
        for title in r[3]:
            path.append({"from": r[0], "rel": "AUTHORED", "to": title})
            path.append({"from": title, "rel": "ABOUT", "to": topic})
    return {"tool": "who_knows",
            "ranking": [{"name": r[0], "role": r[1], "documents": r[2]} for r in rows],
            "path": path}
def record_decision(old_decision_id, new_title, decided_by=None):
    """ACT: record a new decision that supersedes an active one, keeping knowledge current."""
    old = q("MATCH (o:Decision {id:$id}) RETURN o.title, o.status", {"id": old_decision_id})
    if not old:
        return {"tool": "record_decision", "error": f"No decision with id {old_decision_id}", "path": []}
    if old[0][1] != "active":
        newer = q("MATCH (n:Decision)-[:SUPERSEDES]->(:Decision {id:$id}) RETURN n.id, n.title",
                  {"id": old_decision_id})
        path = [{"from_id": n[0], "from": n[1], "rel": "SUPERSEDES",
                 "to_id": old_decision_id, "to": old[0][0]} for n in newer]
        return {"tool": "record_decision",
                "error": f"{old_decision_id} is already superseded by a newer decision. Supersede the latest active decision instead.",
                "path": path}
    proj = q("MATCH (:Decision {id:$id})-[:ABOUT]->(j:Project) RETURN j.name", {"id": old_decision_id})
    if not proj:
        return {"tool": "record_decision", "error": "That decision has no project", "path": []}
    count = q("MATCH (d:Decision) RETURN count(d)")[0][0]
    nid = f"dc{count + 1}"
    from datetime import date
    q("""
        MATCH (o:Decision {id:$old})-[:ABOUT]->(j:Project)
        CREATE (nw:Decision {id:$nid, title:$title, date:$date, status:'active'})
        CREATE (nw)-[:SUPERSEDES]->(o)
        CREATE (nw)-[:ABOUT]->(j)
        SET o.status = 'superseded'
    """, {"old": old_decision_id, "nid": nid, "title": new_title, "date": date.today().isoformat()})
    path = [
        {"from_id": nid, "from": new_title, "rel": "SUPERSEDES", "to_id": old_decision_id, "to": old[0][0]},
        {"from_id": nid, "from": new_title, "rel": "ABOUT", "to": proj[0][0]},
    ]
    if decided_by:
        who = q("MATCH (p:Person {name:$n}) RETURN p.id", {"n": decided_by})
        if who:
            q("MATCH (p:Person {id:$p}), (d:Decision {id:$d}) CREATE (p)-[:DECIDED]->(d)",
              {"p": who[0][0], "d": nid})
            path.append({"from": decided_by, "rel": "DECIDED", "to_id": nid, "to": new_title})
    return {"tool": "record_decision", "new_decision_id": nid,
            "superseded": old[0][0], "path": path}

if __name__ == "__main__":
    print(json.dumps(trace_decision("dc2"), indent=2))
    print(json.dumps(impact_analysis("billing-service"), indent=2))
    print(json.dumps(find_owner("billing-service"), indent=2))
