from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="Groundwater Router API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Endpoints of your backends
BACKEND1_URL = "http://127.0.0.1:8001/ask"    # groundwater availability
BACKEND2_URL = "http://127.0.0.1:8002/query"  # stage of extraction

class QueryRequest(BaseModel):
    query: str

# --- Keyword sets ---
BACKEND1_KEYWORDS = [
    "FRESH", "SALINE", "AVAILABILITY", "UNCONFINED", "CONFINED",
    "SEMI-CONFINED", "TOTAL GROUND WATER", "UA", "TGW", "DC", "IC"
]

BACKEND2_KEYWORDS = [
    "STAGE", "EXTRACTION", "SGWE", "CAU", "ASSESSMENT UNIT", "CATEGORY"
]

def choose_backend(query: str) -> str:
    q = query.upper()

    # check stage-related keywords first
    if any(k in q for k in BACKEND2_KEYWORDS):
        return "backend2"
    if any(k in q for k in BACKEND1_KEYWORDS):
        return "backend1"

    # default → backend1 (general queries)
    return "backend1"

@app.post("/chat")
def chat_router(request: QueryRequest):
    query = request.query
    backend_choice = choose_backend(query)

    if backend_choice == "backend1":
        resp = requests.post(BACKEND1_URL, json={"query": query})
    else:
        resp = requests.post(BACKEND2_URL, json={"query": query})

    return {
        "query": query,
        "backend": backend_choice,
        "answer": resp.json().get("answer", "⚠ No answer returned")
    }

@app.get("/")
def root():
    return {"message": "Router API is running! Use POST /chat with {'query': 'your question'}"}


#.venv\Scripts\activate (.venv) 
#uvicorn router:app --reload --port 8000 (running command)

#C:/projects/C--/.venv/Scripts/Activate.ps1