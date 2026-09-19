# API for fetching quotes!
# Let's implement kinda rate limiting 

import random
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

QUOTE_DATA = []


# CREDIT FOR QUOTES: https://github.com/Osaidii/Quotes-API/
# I asked for his permission to use this and he replied affirmatively!
def load_quotes():
    json_path = Path(__file__).parent / "quotes.json"
    if not json_path.exists():
        raise FileNotFoundError("quotes.json file not found!")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global QUOTE_DATA
    try:
        QUOTE_DATA = load_quotes()
    except Exception as e:
        print(f"Error loading quote: {e}")

    yield

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/api/quote")
@limiter.limit("10/minute")
def harvest(request: Request):
    if not QUOTE_DATA:
        raise HTTPException(status_code=500, detail="No quote available in database.")
    return random.choice(QUOTE_DATA)
