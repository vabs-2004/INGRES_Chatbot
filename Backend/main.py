from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router_router  # the updated unified router

app = FastAPI(title="Unified Groundwater API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unified chat router
app.include_router(router_router)  # no prefix needed → endpoint is /chat

#.venv\Scripts\activate   # Windows
#uvicorn main:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router_router  # the updated unified router

app = FastAPI(title="Unified Groundwater API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unified chat router
app.include_router(router_router)  # no prefix needed → endpoint is /chat

#.venv\Scripts\activate   # Windows
#uvicorn main:app --reload --port 8000
