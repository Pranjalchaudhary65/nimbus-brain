import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

def get_graph(name="company_brain"):
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        username=os.getenv("FALKORDB_USERNAME") or None,
        password=os.getenv("FALKORDB_PASSWORD") or None,
        ssl=os.getenv("FALKORDB_SSL", "false").lower() == "true",
    )
    return db.select_graph(name)