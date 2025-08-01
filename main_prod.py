# plik: main_prod.py (Test 1 - absolutne minimum)
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Test": "Działa"}