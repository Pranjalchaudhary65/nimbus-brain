import os, json
from dotenv import load_dotenv
import time
from openai import OpenAI, InternalServerError, RateLimitError, NotFoundError
from tools import trace_decision, impact_analysis, find_owner
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
]

SYSTEM = ("You are the company brain of Nimbus Labs. Answer ONLY from tool results. "
          "Always use a tool for company questions. Mention the specific decisions, documents "
          "or projects that support your answer. If the tools cannot answer, say so.")
FALLBACK = os.getenv("GEMINI_FALLBACK_MODEL")

def call_llm(messages):
    models = [m for m in [MODEL, FALLBACK] if m]
    last = None
    for attempt in range(4):
        for m in models:
            try:
                return client.chat.completions.create(model=m, messages=messages, tools=TOOLS)
            except (InternalServerError, RateLimitError, NotFoundError) as e:
                last = e
        print(f"  (rate limit or busy, waiting 30s, attempt {attempt + 1}/4)")
        time.sleep(30)
    raise last

def ask(question, user_id="pranjal"):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    path = []
    for _ in range(4):
        resp = call_llm(messages)
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