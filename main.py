from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Import do obsługi plików statycznych

# Importujemy funkcję uruchomienia bazy danych i początkowych danych
from app.core.startup import run_startup_event
# Importujemy routery z naszych modułów
from app.services.router import router as services_router
from app.costs.router import router as costs_router

# Importujemy Base z database.py, aby wywołać create_all
from database import Base, engine

app = FastAPI()

# Dołączanie routerów z poszczególnych modułów
app.include_router(services_router)
app.include_router(costs_router)

# Montowanie katalogu 'static' dla plików statycznych (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup_event():
    # Uruchamiamy funkcję inicjalizacyjną z modułu startup
    run_startup_event()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page_title": "Dashboard"})

