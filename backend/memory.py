import time, uuid
from db import get_graph

g = get_graph()

def save_interaction(user_id, question, answer, path):
    if any(s.get("rel") == "ASKED_ABOUT" for s in path):
        return None   # don't store pure memory lookups
    iid = uuid.uuid4().hex[:10]
    ids, names = set(), set()
    for s in path:
        for k in ("from_id", "to_id"):
            if s.get(k):
                ids.add(s[k])
        for k in ("from", "to"):
            if s.get(k):
                names.add(s[k])
    g.query("""
        MERGE (u:User {id:$u})
        CREATE (i:Interaction {id:$i, question:$q, answer:$a, ts:$ts})
        CREATE (u)-[:ASKED]->(i)
    """, {"u": user_id, "i": iid, "q": question, "a": answer or "", "ts": int(time.time())})
    g.query("""
        MATCH (i:Interaction {id:$i})
        MATCH (e) WHERE e.id IN $ids OR e.name IN $names
        MERGE (i)-[:MENTIONS]->(e)
    """, {"i": iid, "ids": list(ids), "names": list(names)})
    return iid

def recall_memory(entity, user_id="pranjal", limit=3):
    rows = g.query(f"""
        MATCH (u:User {{id:$u}})-[:ASKED]->(i:Interaction)-[:MENTIONS]->(e)
        WHERE e.name = $x OR e.id = $x
        RETURN DISTINCT i.question AS q, i.answer AS a, i.ts AS ts
        ORDER BY ts DESC LIMIT {int(limit)}
    """, {"u": user_id, "x": entity}).result_set
    memories = [{"question": r[0], "answer": r[1], "ts": r[2]} for r in rows]
    return {"tool": "recall_memory", "memories": memories,
            "path": [{"from": user_id, "rel": "ASKED_ABOUT", "to": entity}] if memories else []}