from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

# Importujemy konfigurację bazy produkcyjnej
from database_prod import Base, engine
# Importujemy wszystkie routery
from app.services.router import router as services_router
from app.costs.router import router as costs_router
from app.clients.router import router as clients_router
from app.dashboard.router import router as dashboard_router
from app.calendar.router import router as calendar_router
from app.reports.router import router as reports_router
from app.auth.router import router as auth_router, get_current_user

app = FastAPI()

# Zdarzenie startowe - tworzy tabele w bazie produkcyjnej, jeśli nie istnieją
@app.on_event("startup")
def startup_event():
    # Importujemy modele tutaj, aby mieć pewność, że Base je "widzi"
    import app.services.models
    import app.costs.models
    import app.clients.models
    import app.calendar.models
    Base.metadata.create_all(bind=engine)

# Odczytujemy SECRET_KEY ze zmiennych środowiskowych serwera
SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Montowanie folderów statycznych
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")

# Dołączanie routerów
app.include_router(auth_router)

# Zabezpieczone routery - wymagają zalogowania
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