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
from dotenv import load_dotenv
import os

QUOTE_DATA = []
json_path = Path(__file__).parent / "quotes.json"

# for now -- for testing purpose, im keep this kinda in string here but later i will use .env dwdw
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "realpassword@123") # ERM! if there is no .env it will fall back to the "realpassword@123" but i dont think its happening any time soon

# CREDIT FOR QUOTES: https://github.com/Osaidii/Quotes-API/
# I asked for his(repo's owner) permission to use this and he replied affirmatively!
def load_quotes():
    if not json_path.exists():
        raise FileNotFoundError("quotes.json file not found!")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# small qol for code
def save_quotes():
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(QUOTE_DATA, f, indent=2, ensure_ascii=False)

# checks auth for (PRIVATE) thingies
def check_auth(x_api_key):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

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

# CHANGED add_quote, delete_quote, edit_quote routs into unified quote/{quote_id} where the method determines the action and respected call

# (PUBLIC) this will return a single quote
@app.get("/api/quote")
@limiter.limit("20/minute") # this means only 20 req per min
def harvest(request: Request):
    if not QUOTE_DATA:
        raise HTTPException(status_code=500, detail="No quote available in database.")
    return random.choice(QUOTE_DATA)

# (PUBLIC) this will return quote of that id
@app.get("/api/quote/{quote_id}")
@limiter.limit("20/minute")
def quote_by_id(
    quote_id: int, request: Request
):
    if (quote_id < 0 or quote_id >= len(QUOTE_DATA)):
        raise HTTPException(status_code=404, detail="Quote index not found.")

    return QUOTE_DATA[quote_id]

# (PUBLIC) THis will return all the quotes along with their 0-indexed ids
@app.get("/api/all_quotes")
@limiter.limit("10/minute") # ermm 10 sounds fine for now
def get_all_quotes(request: Request):
    return [
        {"id": index, "quote": quote} for index, quote in enumerate(QUOTE_DATA)
    ]


# (PRIVATE) this will allow us to add quotes
@app.post("/api/quote")
async def add_quote(
    request: Request, x_api_key: str = Header(None)
):
    check_auth(x_api_key)

    data = await request.json()
    new_quote = data.get("quote")

    if not new_quote:
        raise HTTPException(status_code=400, detail="quote is required")

    if new_quote in QUOTE_DATA:
        raise HTTPException(status_code=400, detail="Quote already exists in database.")

    QUOTE_DATA.append(new_quote)

    save_quotes()

    return {"message": "Added!", "quote": new_quote}


# (PRIVATE) this will allow us to delete a quote with given id
@app.delete("/api/quote/{quote_id}")
def delete_quote(
    quote_id: int, request: Request, x_api_key: str = Header(None)
):
    check_auth(x_api_key)

    if quote_id < 0 or quote_id >= len(QUOTE_DATA):
        raise HTTPException(status_code=404, detail="Quote index not found")

    removed = QUOTE_DATA.pop(quote_id)

    save_quotes()

    return {
        "message" : f"Quote of id:{quote_id}, deleted!",
        "deleted_quote": removed
    }


# (PRIVATE) this will allow us to edit the quote of given id
@app.put("/api/quote/{quote_id}")
async def edit_quote(
        quote_id: int, request: Request, x_api_key: str = Header(None)
):
    
    check_auth(x_api_key)
    
    if quote_id < 0 or quote_id >= len(QUOTE_DATA):
        raise HTTPException(status_code=404, detail="Quote index not found")

    data = await request.json()
    updated_quote = data.get("quote")

    if not updated_quote:
        raise HTTPException(status_code=400, detail="Quote is required")

    QUOTE_DATA[quote_id] = updated_quote

    save_quotes()

    return {
        "message": f"Quote of index: {quote_id}, updated!",
        "id": quote_id,
        "quote": updated_quote
    }