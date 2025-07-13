from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Import do obsługi plików statycznych
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse

# Importujemy funkcję uruchomienia bazy danych i początkowych danych
from app.core.startup import run_startup_event
# Importujemy routery z naszych modułów
from app.services.router import router as services_router
from app.costs.router import router as costs_router

# Importujemy Base z database.py, aby wywołać create_all
from database import Base, engine

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")
templates = Jinja2Templates(directory="templates")

# Dołączanie routerów z poszczególnych modułów
app.include_router(services_router)
app.include_router(costs_router)

@app.on_event("startup")
def startup_event():
    # Uruchamiamy funkcję inicjalizacyjną z modułu startup
    run_startup_event()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page_title": "Dashboard"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard"})

@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request, "title": "Klienci"})

@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request):
    return templates.TemplateResponse("invoices.html", {"request": request, "title": "Faktury"})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "title": "Ustawienia"})

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request, exc: ResponseValidationError):
    # pokaż w body dokładnie, czego brakuje
    return JSONResponse(
        status_code=500,
        content={
            "error": "Invalid response schema",
            "details": exc.errors(),
            "body": exc.body
        }
    )