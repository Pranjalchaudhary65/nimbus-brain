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

if __name__ == "__main__":
    print(json.dumps(trace_decision("dc2"), indent=2))
    print(json.dumps(impact_analysis("billing-service"), indent=2))
    print(json.dumps(find_owner("billing-service"), indent=2))
