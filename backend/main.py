import random
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def load_quotes():
    json_path = Path(__file__).parent / "quotes.json"
    if not json_path.exists():
        raise FileNotFoundError("quote.json file not found!")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
    quotes = load_quotes()
    return random.choice(quotes)
