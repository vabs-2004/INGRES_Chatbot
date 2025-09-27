from fastapi import APIRouter
from pydantic import BaseModel
from backend1 import ask as backend1_ask
from backend2 import query as backend2_query

router_router = APIRouter()

# Input model
class QueryRequest(BaseModel):
    query: str

# Keyword lists to decide backend
BACKEND1_KEYWORDS = [
    "FRESH", "SALINE", "AVAILABILITY", "UNCONFINED", "CONFINED",
    "SEMI-CONFINED", "TOTAL GROUND WATER", "UA", "TGW", "DC", "IC"
]

BACKEND2_KEYWORDS = [
    "STAGE", "EXTRACTION", "SGWE", "CAU", "ASSESSMENT UNIT", "CATEGORY"
]

# Decide backend based on query
def choose_backend(query: str) -> str:
    q = query.upper()
    if any(k in q for k in BACKEND2_KEYWORDS):
        return "backend2"
    if any(k in q for k in BACKEND1_KEYWORDS):
        return "backend1"
    return "backend1"

# --- Unified /chat endpoint ---
@router_router.post("/chat")
def chat_endpoint(request: QueryRequest):
    query = request.query
    backend_choice = choose_backend(query)

    if backend_choice == "backend1":
        answer = backend1_ask(query)
    else:
        answer = backend2_query(query)

    return {
        "query": query,
        "backend": backend_choice,
        "answer": answer
    }

# Optional root GET
@router_router.get("/")
def root():
    return {"message": "Router API is running! Use POST /chat with {'query': 'your question'}"}
