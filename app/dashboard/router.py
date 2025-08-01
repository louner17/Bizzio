from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi.templating import Jinja2Templates
from app.core.dependencies import get_db
from app.services import crud as services_crud
from app.costs import crud as costs_crud
from app.clients import crud as clients_crud
from app.calendar import crud as calendar_crud

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Wyświetla stronę HTML dashboardu."""
    return templates.TemplateResponse("dashboard.html", {"request": request, "page_title": "Dashboard"})


@router.get("/dashboard/api")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Zbiera, agreguje i zwraca wszystkie dane potrzebne do wyświetlenia na dashboardzie.
    """
    today = datetime.now().date()
    start_of_current_month = today.replace(day=1)
    end_of_current_month = start_of_current_month + relativedelta(months=1, days=-1)

    # --- 1. Obliczenia dla Kart KPI (Bieżący Miesiąc) ---
    today = datetime.today()
    start_of_current_month = today.replace(day=1)

    # Pobranie danych z bieżącego miesiąca
    monthly_services = services_crud.get_services(db, start_date=start_of_current_month, end_date=today)
    monthly_revenue = sum(s.base_price_net for s in monthly_services)

    monthly_costs = costs_crud.get_expenses(db)  # Na razie pobieramy wszystkie, filtrujemy poniżej

    # Filtrowanie kosztów po stronie Pythona
    monthly_costs_filtered = [c for c in monthly_costs if c.invoice_date >= start_of_current_month.date()]

    # Obliczenia
    tomorrow = today + relativedelta(days=1)
    future_appointments = calendar_crud.get_appointments(db, start=datetime.combine(tomorrow, datetime.min.time()),
                                                end=datetime.combine(end_of_current_month, datetime.max.time()))
    potential_revenue = sum(app.price for app in future_appointments if app.status == 'zaplanowana')
    monthly_revenue = sum(s.base_price_net for s in monthly_services)
    monthly_total_costs = sum(c.amount_gross for c in monthly_costs_filtered)
    monthly_profit = monthly_revenue - monthly_total_costs

    # --- 2. Dane do Wykresu Przychody vs Koszty (Ostatnie 6 Miesięcy) ---
    labels = []
    revenue_data = []
    costs_data = []

    for i in range(5, -1, -1):
        # Obliczanie zakresu dat dla każdego z 6 miesięcy
        month_date = today - relativedelta(months=i)
        start_of_month = month_date.replace(day=1)
        end_of_month = start_of_month + relativedelta(months=1, days=-1)

        labels.append(start_of_month.strftime("%b %Y"))  # Np. "Lip 2025"

        # Przychody w danym miesiącu
        month_revenue = sum(
            s.base_price_net for s in services_crud.get_services(db, start_date=start_of_month, end_date=end_of_month))
        revenue_data.append(month_revenue)

        # Koszty w danym miesiącu
        month_costs = sum(c.amount_gross for c in costs_crud.get_expenses(db) if
                          start_of_month.date() <= c.invoice_date <= end_of_month.date())
        costs_data.append(month_costs)

    revenue_vs_costs_chart = {
        "labels": labels,
        "revenue": revenue_data,
        "costs": costs_data
    }

    # --- 3. Dane do Wykresu Struktury Przychodów (Całkowite) ---
    all_services = services_crud.get_services(db)
    revenue_by_category = {}
    for service in all_services:
        category_name = service.service_type.category.name
        revenue_by_category[category_name] = revenue_by_category.get(category_name, 0) + service.base_price_net

    revenue_structure_chart = {
        "labels": list(revenue_by_category.keys()),
        "data": list(revenue_by_category.values())
    }

    # --- 4. Lista Nadchodzących Płatności ---
    all_costs = costs_crud.get_expenses(db)
    upcoming_payments = [
        {"description": c.description, "due_date": c.due_date.isoformat(), "amount": c.amount_gross}
        for c in all_costs if not c.is_paid
    ]
    # Sortowanie po terminie płatności i wzięcie pierwszych 5
    upcoming_payments = sorted(upcoming_payments, key=lambda p: p['due_date'])[:5]

    return {
        "kpi": {
            "profit": monthly_profit,
            "revenue": monthly_revenue,
            "costs": monthly_total_costs,
            "potential_revenue": potential_revenue
        },
        "revenue_vs_costs_chart": revenue_vs_costs_chart,
        "revenue_structure_chart": revenue_structure_chart,
        "upcoming_payments": upcoming_payments
    }