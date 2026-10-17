# Nimbus Brain: a Company Brain with graph memory on FalkorDB

An AI agent that answers questions about a company by **following connections in a
FalkorDB graph**: who owns what, why a decision was made, what breaks if a service
changes, and what the user asked before. Every answer comes back with the **path of
nodes and edges** that produced it. All data is synthetic (a fictional company,
Nimbus Labs).

**Tracks:** Company Brain, Agent Memory and Coordination

**Demo video:** (link added at submission)
**Live deployment:** (link added at submission, or use the local setup below)

## Why FalkorDB is essential

- Every answer is a multi-hop graph traversal (decision history, dependency chains,
  ownership). The LLM only chooses a tool and writes the final sentence.
- Memory is stored in the graph as `User` and `Interaction` nodes linked to the
  projects, people and decisions they mention, so recall is a traversal.
- Without FalkorDB there is nothing for the agent to query, so the product does not work.

## Graph data model

| Node | Properties |
|---|---|
| Person | id, name, role |
| Team | id, name |
| Project | id, name |
| Document | id, title, date, text |
| Decision | id, title, date, status |
| Topic | id, name |
| User (memory) | id |
| Interaction (memory) | id, question, answer, ts |

| Relationship | Meaning |
|---|---|
| (Person)-[:MEMBER_OF]->(Team) | team membership |
| (Person)-[:OWNS]->(Project) | project owner |
| (Project)-[:DEPENDS_ON]->(Project) | dependencies |
| (Person)-[:AUTHORED]->(Document) | who wrote it |
| (Document)-[:ABOUT]->(Topic) | what it covers |
| (Document)-[:MENTIONS]->(Project) | projects it mentions |
| (Person)-[:DECIDED]->(Decision) | who decided |
| (Decision)-[:ABOUT]->(Project) | what it affects |
| (Decision)-[:BASED_ON]->(Document) | the evidence |
| (Decision)-[:SUPERSEDES]->(Decision) | newer replaces older |
| (User)-[:ASKED]->(Interaction) | what a user asked |
| (Interaction)-[:MENTIONS]->(any node) | what the question involved |

## Key Cypher queries

Why was a decision made (follows `SUPERSEDES` and `BASED_ON`, up to 3 hops):

```cypher
MATCH p=(d:Decision {id:$id})-[:SUPERSEDES|BASED_ON*1..3]->(x)
UNWIND relationships(p) AS r
RETURN DISTINCT startNode(r).id, endNode(r).id, type(r)
```

What breaks if a project changes (dependency chain, up to 3 hops):

```cypher
MATCH p=(j:Project {name:$n})<-[:DEPENDS_ON*1..3]-(x:Project)
RETURN x.name, min(length(p))
```

Who owns a project and which team they are on:

```cypher
MATCH (p:Person)-[:OWNS]->(j:Project {name:$n})
OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
RETURN p.name, p.role, t.name
```

Recall what a user asked earlier about an entity (persistent memory):

```cypher
MATCH (u:User {id:$u})-[:ASKED]->(i:Interaction)-[:MENTIONS]->(e)
WHERE e.name = $x OR e.id = $x
RETURN DISTINCT i.question, i.answer, i.ts ORDER BY i.ts DESC
```

## Architecture

- `backend/seed.py`: synthetic company data
- `backend/load_graph.py`: loads the data into FalkorDB
- `backend/tools.py`: graph tools that return an answer plus its path
- `backend/memory.py`: saves and recalls interactions in the graph
- `backend/agent.py`: Gemini function calling picks a tool, runs it, and writes the answer

## Setup

1. Create a free FalkorDB Cloud instance at app.falkordb.cloud, or run FalkorDB
   locally with `docker run -p 6379:6379 -p 3000:3000 --rm falkordb/falkordb`
   (local: host `localhost`, port `6379`, empty password, `FALKORDB_SSL=false`).
2. Get a free Gemini API key from Google AI Studio.
3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your own values.
5. Load the graph and run the agent:

```bash
cd backend
python load_graph.py          # expect: Nodes: 50, Edges: 96
python agent.py               # asks three sample questions
python memory_demo.py ask     # then, in a separate run:
python memory_demo.py recall  # shows memory surviving between runs
```

## Example

Question: "Why did we choose Adyen for EU payments?" The agent calls `trace_decision`,
returns the decision, the older Stripe decision it replaced, and the documents behind
both (5 links), and writes its answer from exactly those results.

## Data

All data is synthetic and created for this project. No private or restricted data is used.

## AI tools used

Disclosure: AI assistants (Claude) were used for guidance, to draft parts of the code,
and to explain concepts. The team ran, tested and reviewed the code and can explain
the graph model, the queries and the architecture.

## Team

(Add the names of all 3 team members.)