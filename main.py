import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

# Importujemy funkcję uruchomienia bazy danych i początkowych danych
from app.core.startup import run_startup_event
from app.auth.router import router as auth_router, get_current_user
from app.services.router import router as services_router
from app.costs.router import router as costs_router
from app.clients.router import router as clients_router
from app.dashboard.router import router as dashboard_router
from app.calendar.router import router as calendar_router
from app.reports.router import router as reports_router

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY", "domyslny_sekret_do_testow_lokalnych")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Montowanie folderów statycznych
os.makedirs("static", exist_ok=True)
os.makedirs("attachments", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")
templates = Jinja2Templates(directory="templates")

# Dołączanie routerów
app.include_router(auth_router)
app.include_router(dashboard_router, dependencies=[Depends(get_current_user)])
app.include_router(calendar_router, dependencies=[Depends(get_current_user)])
app.include_router(services_router, dependencies=[Depends(get_current_user)])
app.include_router(costs_router, dependencies=[Depends(get_current_user)])
app.include_router(clients_router, dependencies=[Depends(get_current_user)])
app.include_router(reports_router, dependencies=[Depends(get_current_user)])

@app.on_event("startup")
def startup_event():
    run_startup_event()
    pass

# Główna strona, która przekierowuje do panelu
@app.get("/", response_class=RedirectResponse, dependencies=[Depends(get_current_user)])
async def read_root():
    return RedirectResponse(url="/dashboard")
