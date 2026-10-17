import os, json
from dotenv import load_dotenv
import time
from openai import OpenAI, InternalServerError, RateLimitError, NotFoundError
from tools import trace_decision, impact_analysis, find_owner, who_knows, record_decision
from memory import save_interaction, recall_memory

load_dotenv()
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)
MODEL = os.getenv("GEMINI_MODEL")

TOOL_FUNCS = {
    "trace_decision": trace_decision,
    "impact_analysis": impact_analysis,
    "find_owner": find_owner,
        "recall_memory": recall_memory,
            "who_knows": who_knows,
                "record_decision": record_decision,
}

PROJECTS = "auth-service, billing-service, checkout-api, notification-service, analytics-pipeline, search-service, web-app, mobile-app"

TOOLS = [
    {"type": "function", "function": {
        "name": "trace_decision",
        "description": "Explain WHY a decision was made by tracing it back to the older decisions and documents it was based on. "
                       "Decision ids: dc1 Stripe for payments, dc2 Adyen for EU payments, dc3 Auth0, "
                       "dc4 in-house authentication, dc5 Postgres for analytics, dc6 ClickHouse for analytics.",
        "parameters": {"type": "object",
                       "properties": {"decision_id": {"type": "string"}},
                       "required": ["decision_id"]}}},
    {"type": "function", "function": {
        "name": "impact_analysis",
        "description": f"Find WHAT BREAKS or is affected if a project changes. Project names: {PROJECTS}.",
        "parameters": {"type": "object",
                       "properties": {"project_name": {"type": "string"}},
                       "required": ["project_name"]}}},
    {"type": "function", "function": {
        "name": "find_owner",
        "description": f"Find WHO owns a project and which team they are on. Project names: {PROJECTS}.",
        "parameters": {"type": "object",
                       "properties": {"project_name": {"type": "string"}},
                       "required": ["project_name"]}}},
                           {"type": "function", "function": {
        "name": "recall_memory",
        "description": "Recall what this user asked and what was answered EARLIER (in past sessions) about a project, decision or person. "
                       "Use when the user asks what was discussed or asked before. entity is a project name, person name or decision id.",
        "parameters": {"type": "object",
                       "properties": {"entity": {"type": "string"}},
                       "required": ["entity"]}}},
                           {"type": "function", "function": {
        "name": "who_knows",
        "description": "Find WHO knows most about a topic, ranked by the documents they wrote about it. "
                       "Topic names: payments, authentication, vendor-selection, database, security, scaling.",
        "parameters": {"type": "object",
                       "properties": {"topic": {"type": "string"}},
                       "required": ["topic"]}}},
                           {"type": "function", "function": {
        "name": "record_decision",
        "description": "ACT on the graph: record a NEW decision that replaces an existing ACTIVE decision, "
                       "so company knowledge stays current. Use when the user says the company decided or changed something. "
                       "old_decision_id must be an active decision: dc2 (Adyen for EU payments), dc4 (in-house authentication), "
                       "dc6 (ClickHouse for analytics). new_title is the new decision. decided_by is an optional person name. "
                       "The result contains new_decision_id, which can be traced later with trace_decision.",
        "parameters": {"type": "object",
                       "properties": {"old_decision_id": {"type": "string"},
                                      "new_title": {"type": "string"},
                                      "decided_by": {"type": "string"}},
                       "required": ["old_decision_id", "new_title"]}}},
]

SYSTEM = ("You are the company brain of Nimbus Labs. Answer ONLY from tool results. "
          "Always use a tool for company questions. Mention the specific decisions, documents "
          "or projects that support your answer. If the tools cannot answer, say so. "
          "If a tool returns an error, explain the error to the user in plain words and STOP. "
          "Do not retry the same action or call extra tools to work around it.")
FALLBACK = os.getenv("GEMINI_FALLBACK_MODEL")

def call_llm(messages, use_tools=True):
    models = [m for m in [MODEL, FALLBACK] if m]
    last = None
    for attempt in range(4):
        for m in models:
            try:
                kwargs = {"model": m, "messages": messages}
                if use_tools:
                    kwargs["tools"] = TOOLS
                return client.chat.completions.create(**kwargs)
            except (InternalServerError, RateLimitError, NotFoundError) as e:
                last = e
        print(f"  (rate limit or busy, waiting 30s, attempt {attempt + 1}/4)")
        time.sleep(30)
    raise last

def ask(question, user_id="pranjal"):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    path = []
    for step in range(6):
        final = (step == 5)          # last turn: force a written answer, no more tools
        if final:
            messages.append({"role": "user",
                             "content": "Now write the final answer using only the tool results above. Do not call tools."})
        resp = call_llm(messages, use_tools=not final)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            save_interaction(user_id, question, msg.content, path)
            return {"answer": msg.content, "path": path}
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            if call.function.name == "recall_memory":
                args["user_id"] = user_id
            result = TOOL_FUNCS[call.function.name](**args)
            path.extend(result.get("path", []))
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return {"answer": "I could not finish.", "path": path}

if __name__ == "__main__":
    for question in ["Why did we choose Adyen for EU payments?",
                     "What breaks if billing-service changes?",
                     "Who owns billing-service?"]:
        out = ask(question)
        print("\nQ:", question)
        print("A:", out["answer"])
        print("PATH:", len(out["path"]), "links")