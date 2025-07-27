# plik: main_no_db.py (TYLKO DO DEBUGOWANIA)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Montujemy pliki statyczne, to jest bezpieczne
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Definiujemy ścieżki do wszystkich Twoich stron,
# ale zamiast pobierać dane z bazy, przekazujemy puste listy.

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Prosta strona startowa, bo logowanie jest wyłączone
    return HTMLResponse("<h1>Aplikacja startuje (bez bazy danych)</h1>")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    # Serwujemy szablon z pustymi danymi
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard"})

@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request, "title": "Kalendarz"})

@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request):
    return templates.TemplateResponse("services.html", {"request": request, "title": "Usługi", "service_types": []})

@app.get("/costs/", response_class=HTMLResponse)
async def costs_page(request: Request):
    return templates.TemplateResponse("costs.html", {"request": request, "title": "Koszty", "contractors": [], "expense_categories": []})

@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request, "title": "Klienci"})

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "title": "Raporty"})

# Inne strony można dodać w ten sam sposób