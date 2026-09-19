# API for fetching quotes!
# Let's implement kinda rate limiting 

import random
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

QUOTE_DATA = []

# for now -- for testing purpose, im keep this kinda in string here but later i will use .env dwdw
SECRET_KEY = "test"

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


# (PUBLIC) this will return a single quote
@app.get("/api/quote")
@limiter.limit("10/minute") # this means only 10 req per min
def harvest(request: Request):
    if not QUOTE_DATA:
        raise HTTPException(status_code=500, detail="No quote available in database.")
    return random.choice(QUOTE_DATA)


# (PUBLIC) THis will return all the quotes along with their 0-indexed ids
@app.get("/api/all_quotes")
@limiter.limit("10/minute") # ermm 10 sounds fine for this one too
def get_all_quotes(request: Request):
    return [
        {"id": index, "quote": quote} for index, quote in enumerate(QUOTE_DATA)
    ]


# (PRIVATE) this will allow us to add quotes
@app.post("/api/add_quote")
async def add_quote(
    request: Request, x_api_key: str = Header(None)
):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    new_quote = data.get("quote")

    if not new_quote:
        raise HTTPException(status_code=400, detail="quote is required")

    QUOTE_DATA.append(new_quote)
    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(QUOTE_DATA, f, indent=2, ensure_ascii=False)

    return {"message": "Added!", "quote": new_quote}
