from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os, requests

# Load environment variables
load_dotenv()
TRANSLATE_API = os.getenv("TRANSLATE_API")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware so React can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic model for request body
class TranslateRequest(BaseModel):
    q: str
    target: str = "hi"

# Translation endpoint
@app.post("/translate")
def translate_text(payload: TranslateRequest):
    response = requests.post(
        f"https://translation.googleapis.com/language/translate/v2?key={TRANSLATE_API}",
        headers={"Content-Type": "application/json"},
        json={"q": payload.q, "target": payload.target, "format": "text"},
    )
    return response.json()
