# plik: app/reports/router.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from fastapi.templating import Jinja2Templates

from app.core.dependencies import get_db
from app.services import models as services_models
from app.costs import models as costs_models
from app.clients import models as clients_models
from app.calendar import models as calendar_models  # Upewnijmy się, że ten import jest

router = APIRouter(tags=["Reports"])

templates = Jinja2Templates(directory="templates")

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "page_title": "Raporty"})

@router.get("/api/reports")
async def get_reports_data(period: str = '3m', db: Session = Depends(get_db)):
    today = date.today()
    start_date = None

    if period == '1m':
        start_date = today.replace(day=1)
    elif period == '3m':
        start_date = today - relativedelta(months=3)
    elif period == '6m':
        start_date = today - relativedelta(months=6)
    elif period == '1y':
        start_date = today - relativedelta(years=1)
    elif period == '2y':
        start_date = today - relativedelta(years=2)

    # --- 1. Raporty Historyczne (bez zmian) ---
    monthly_financials = defaultdict(lambda: {'revenue': 0, 'costs': 0})
    revenue_query = db.query(
        func.strftime('%Y-%m', services_models.Service.date).label('month'),
        func.sum(services_models.Service.base_price_net).label('total_revenue')
    )
    if start_date:
        revenue_query = revenue_query.filter(services_models.Service.date >= start_date)
    for month, total_revenue in revenue_query.group_by('month').all():
        monthly_financials[month]['revenue'] = total_revenue or 0

    costs_query = db.query(
        func.strftime('%Y-%m', costs_models.Expense.invoice_date).label('month'),
        func.sum(costs_models.Expense.amount_gross).label('total_costs')
    )
    if start_date:
        costs_query = costs_query.filter(costs_models.Expense.invoice_date >= start_date)
    for month, total_costs in costs_query.group_by('month').all():
        monthly_financials[month]['costs'] = total_costs or 0

    sorted_months = sorted(monthly_financials.keys())
    financial_summary_data = {
        "labels": sorted_months,
        "revenue": [monthly_financials[m]['revenue'] for m in sorted_months],
        "costs": [monthly_financials[m]['costs'] for m in sorted_months],
        "profit": [(monthly_financials[m]['revenue'] - monthly_financials[m]['costs']) for m in sorted_months]
    }

    expense_query = db.query(costs_models.ExpenseCategory.name, func.sum(costs_models.Expense.amount_gross)).join(
        costs_models.ExpenseCategory)
    if start_date:
        expense_query = expense_query.filter(costs_models.Expense.invoice_date >= start_date)
    expense_breakdown_data = expense_query.group_by(costs_models.ExpenseCategory.name).all()

    revenue_query = db.query(services_models.Category.name,
                             func.sum(services_models.Service.base_price_net)).select_from(
        services_models.Service).join(services_models.ServiceType).join(services_models.Category)
    if start_date:
        revenue_query = revenue_query.filter(services_models.Service.date >= start_date)
    revenue_structure_data = revenue_query.group_by(services_models.Category.name).all()

    popularity_query = db.query(services_models.ServiceType.name, func.count(services_models.Service.id)).join(
        services_models.ServiceType)
    if start_date:
        popularity_query = popularity_query.filter(services_models.Service.date >= start_date)
    service_popularity_data = popularity_query.group_by(services_models.ServiceType.name).order_by(
        desc(func.count(services_models.Service.id))).all()

    source_query = db.query(clients_models.Client.source, func.count(clients_models.Client.id)).filter(
        clients_models.Client.source.isnot(None))
    if start_date:
        source_query = source_query.filter(clients_models.Client.date_added >= start_date)
    client_source_data = source_query.group_by(clients_models.Client.source).all()

    # --- NOWA, ZOPTYMALIZOWANA LOGIKA DLA RAPORTÓW PROGNOSTYCZNYCH ---
    future_appointments = db.query(calendar_models.Appointment).join(
        services_models.ServiceType
    ).join(
        services_models.Category  # Dodajemy join do kategorii
    ).filter(
        calendar_models.Appointment.start_time > today,
        calendar_models.Appointment.status == 'zaplanowana'
    ).all()

    forecast_revenue_by_month = defaultdict(float)
    forecast_services_by_type = defaultdict(int)
    forecast_trend_by_category_and_month = defaultdict(lambda: defaultdict(int))
    three_months_later = today + relativedelta(months=3)

    for app in future_appointments:
        month_key = app.start_time.strftime('%Y-%m')
        service_type_name = app.service_type.name
        category_name = app.service_type.category.name
        forecast_revenue_by_month[month_key] += app.price

        if app.start_time.date() < three_months_later:
            forecast_services_by_type[service_type_name] += 1

        forecast_trend_by_category_and_month[category_name][month_key] += 1

    sorted_revenue_months = sorted(forecast_revenue_by_month.keys())
    forecasted_revenue_data = {
        "labels": sorted_revenue_months,
        "data": [forecast_revenue_by_month[m] for m in sorted_revenue_months]
    }

    sorted_services = sorted(forecast_services_by_type.items(), key=lambda item: item[1], reverse=True)[:10]
    forecasted_services_data = {
        "labels": [item[0] for item in sorted_services],
        "data": [item[1] for item in sorted_services]
    }

    all_months = sorted(
        list(set(month for categories in forecast_trend_by_category_and_month.values() for month in categories.keys())))
    all_categories = list(forecast_trend_by_category_and_month.keys())

    trend_datasets = []
    for category_name in all_categories:
        counts = [forecast_trend_by_category_and_month[category_name].get(month, 0) for month in all_months]

        # Pobierz kolor przypisany do kategorii
        category_obj = db.query(services_models.Category).filter(services_models.Category.name == category_name).first()
        color = category_obj.color if category_obj else '#A0AEC0'

        trend_datasets.append({
            "label": category_name,  # Etykieta to teraz kategoria
            "data": counts,
            "borderColor": color,  # Używamy koloru z bazy
            "backgroundColor": color.replace(')', ', 0.1)').replace('rgb', 'rgba'),  # Dodajemy przezroczystość
            "fill": False,
            "tension": 0.2
        })

    forecasted_service_count_data = {
        "labels": all_months,
        "datasets": trend_datasets
    }

    return {
        "financial_summary": financial_summary_data,
        "expense_breakdown": {"labels": [r[0] for r in expense_breakdown_data],
                              "data": [r[1] for r in expense_breakdown_data]},
        "revenue_structure": {"labels": [r[0] for r in revenue_structure_data],
                              "data": [r[1] for r in revenue_structure_data]},
        "service_popularity": {"labels": [r[0] for r in service_popularity_data],
                               "data": [r[1] for r in service_popularity_data]},
        "client_sources": {"labels": [r[0] for r in client_source_data], "data": [r[1] for r in client_source_data]},
        "forecasted_revenue": forecasted_revenue_data,
        "forecasted_services": forecasted_services_data,
        "forecasted_service_count": forecasted_service_count_data
    }