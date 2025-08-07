from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
import os

from database_prod import Base, engine
from app.auth.router import get_current_user
from app.services.router import router as services_router
from app.costs.router import router as costs_router
from app.clients.router import router as clients_router
from app.dashboard.router import router as dashboard_router
from app.calendar.router import router as calendar_router
from app.reports.router import router as reports_router
from app.auth.router import router as auth_router

app = FastAPI()

@app.on_event("startup")
def startup_event():
    import app.services.models, app.costs.models, app.clients.models, app.calendar.models
    Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

os.makedirs("static", exist_ok=True)
os.makedirs("attachments", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")
templates = Jinja2Templates(directory="templates")

# Dołączanie routerów
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(calendar_router)
app.include_router(services_router)
app.include_router(costs_router)
app.include_router(clients_router)
app.include_router(reports_router)

# Główna strona
@app.get("/")
async def read_root(request: Request):
    # Sprawdzamy sesję ręcznie, aby uniknąć błędu przy pierwszym wejściu
    if not request.session.get('user'):
        return RedirectResponse(url='/login')
    return RedirectResponse(url="/dashboard")