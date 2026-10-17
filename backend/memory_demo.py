import sys
from agent import ask

if len(sys.argv) < 2:
    print("Use: python memory_demo.py ask   or   python memory_demo.py recall")
    sys.exit()

q = "Who owns billing-service?" if sys.argv[1] == "ask" else "What did we discuss earlier about billing-service?"
out = ask(q, user_id="pranjal")
print("Q:", q)
print("A:", out["answer"])
print("PATH:", out["path"])