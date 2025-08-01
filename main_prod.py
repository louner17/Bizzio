# plik: main_prod.py (Test 3 - dodajemy bazę)
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
import os

from database_prod import Base, get_engine
from app.auth.router import router as auth_router

app = FastAPI()

@app.on_event("startup")
def startup_event():
    eng = get_engine() # Pobieramy silnik
    import app.services.models, app.costs.models, app.clients.models, app.calendar.models
    Base.metadata.create_all(bind=eng)

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"Test": "Działa"}