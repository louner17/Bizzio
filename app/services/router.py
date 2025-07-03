from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import datetime

# Importujemy zależności z naszego nowego modułu core
from app.core.dependencies import get_db

# Importujemy CRUD i modele z bieżącego modułu services
import app.services.crud as crud
import app.services.schemas as schemas

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/services", response_class=HTMLResponse)
async def list_services(request: Request, db: Session = Depends(get_db)):
    """Wyświetla listę wszystkich usług oraz formularz do dodawania nowej."""
    services = crud.get_services(db)
    service_types = crud.get_service_types(db)
    categories = crud.get_categories(db)
    vat_rates = crud.get_vat_rates(db)
    initial_date = datetime.date.today().strftime('%Y-%m-%d')
    return templates.TemplateResponse("services.html", {
        "request": request,
        "services": services,
        "service_types": service_types,
        "categories": categories,
        "vat_rates": vat_rates,
        "initial_date": initial_date,
        "page_title": "Usługi"
    })

@router.get("/api/services", response_model=List[Dict[str, Any]])
async def get_services_api(db: Session = Depends(get_db)):
    services = crud.get_services(db)
    return [
        {
            "id": s.id,
            "date": s.date.isoformat(),
            "base_price_net": s.base_price_net,
            "service_type": {
                "id": s.service_type.id,
                "name": s.service_type.name,
                "category_id": s.service_type.category_id,
                "vat_rate_id": s.service_type.vat_rate_id
            }
        } for s in services
    ]

@router.get("/api/service_types", response_model=List[Dict[str, Any]])
async def get_service_types_api(db: Session = Depends(get_db)):
    service_types = crud.get_service_types(db)
    return [
        {
            "name": st.name,
            "category": {
                "id": st.category.id,
                "name": st.category.name
            },
            "vat_rate_id": st.vat_rate_id
        } for st in service_types
    ]

@router.get("/api/categories", response_model=List[Dict[str, Any]])
async def get_categories_api(db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    return [
        {
            "id": c.id,
            "name": c.name
        } for c in categories
    ]

@router.post("/services/add", response_model=schemas.ServiceDisplay, status_code=status.HTTP_201_CREATED)
async def add_service(
        service_data: schemas.ServiceCreate,
        db: Session = Depends(get_db)
):
    db_service = crud.create_service(
        db=db,
        service_type_id=service_data.service_type_id,
        date=service_data.date,
        price=service_data.base_price_net  # Cena z pola base_price_net
    )
    return db_service

@router.post("/service_types/add", response_class=RedirectResponse)
async def add_service_type(
        name: str = Form(...),
        category_id: int = Form(...),
        vat_rate_id: int = Form(...),
        db: Session = Depends(get_db)
):
    crud.get_or_create_service_type(db=db, name=name, category_id=category_id, vat_rate_id=vat_rate_id)
    return RedirectResponse(url="/services", status_code=303)

@router.post("/categories/add", response_class=RedirectResponse)
async def add_category(
        name: str = Form(...),
        db: Session = Depends(get_db)
):
    crud.get_or_create_category(db=db, name=name)
    return RedirectResponse(url="/services", status_code=303)