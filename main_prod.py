# plik: main_prod.py (Test 2 - dodajemy auth)
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os
from app.auth.router import router as auth_router

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"Test": "Działa"}