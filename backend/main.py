import random
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

QUOTE_DATA = []

def load_quotes():
    json_path = Path(__file__).parent / "quotes.json"
    if not json_path.exists():
        raise FileNotFoundError("quote.json file not found!")
    
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

app = FastAPI()

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
def harvest():
    if not QUOTE_DATA:
        raise HTTPException(status_code=500, detail="No quote available in database.")
    return random.choice(QUOTE_DATA)
