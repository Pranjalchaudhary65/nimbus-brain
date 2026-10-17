import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import ask

BASE = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Nimbus Brain")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Question(BaseModel):
    question: str
    user_id: str = "pranjal"

@app.post("/ask")
def ask_endpoint(body: Question):
    return ask(body.question, body.user_id)

@app.get("/")
def home():
    return FileResponse(os.path.join(BASE, "static", "index.html"))