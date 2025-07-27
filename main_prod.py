# plik: main_prod.py
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

# WAŻNA ZMIANA: Importujemy z nowego pliku bazy danych
from database_prod import Base, engine, SessionLocal
from app.auth.router import get_current_user
# Importy wszystkich routerów...
from app.services.router import router as services_router
from app.costs.router import router as costs_router
from app.clients.router import router as clients_router
from app.dashboard.router import router as dashboard_router
from app.calendar.router import router as calendar_router
from app.reports.router import router as reports_router
from app.auth.router import router as auth_router

app = FastAPI()

# Zdarzenie startowe - tworzy tabele w bazie produkcyjnej
@app.on_event("startup")
def startup_event():
    # Importujemy wszystkie modele, aby Base je "zobaczył"
    import app.services.models
    import app.costs.models
    import app.clients.models
    import app.calendar.models
    Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")

app.include_router(auth_router)

# Zabezpieczone routery
app.include_router(dashboard_router, dependencies=[Depends(get_current_user)])
app.include_router(calendar_router, dependencies=[Depends(get_current_user)])
app.include_router(services_router, dependencies=[Depends(get_current_user)])
app.include_router(costs_router, dependencies=[Depends(get_current_user)])
app.include_router(clients_router, dependencies=[Depends(get_current_user)])
app.include_router(reports_router, dependencies=[Depends(get_current_user)])

# Główna strona, która przekierowuje do panelu
@app.get("/", response_class=RedirectResponse, dependencies=[Depends(get_current_user)])
async def read_root():
    return RedirectResponse(url="/dashboard")