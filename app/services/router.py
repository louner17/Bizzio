from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
from datetime import date
import datetime

# Importujemy zależności z naszego nowego modułu core
from app.core.dependencies import get_db

# Importujemy CRUD i modele z bieżącego modułu services
import app.services.crud as crud
import app.services.schemas as schemas
import app.services.models as models

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
async def get_services_api(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    services = crud.get_services(db, start_date=start_date, end_date=end_date)
    return [
        {
            "id": s.id,
            "date": s.date.isoformat(),
            "base_price_net": s.base_price_net,
            "service_type": {
                "id": s.service_type.id,
                "name": s.service_type.name
            }
        } for s in services
    ]

@router.get("/api/services/{service_id}", response_model=schemas.ServiceRecord)
async def get_service_api(service_id: int, db: Session = Depends(get_db)):
    """Pobiera dane pojedynczej usługi."""
    db_service = crud.get_service(db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Usługa nie znaleziona")
    return db_service

@router.put("/api/services/{service_id}", response_model=schemas.ServiceRecord)
async def update_service_api(service_id: int, data: schemas.ServiceCreate, db: Session = Depends(get_db)):
    """Aktualizuje istniejącą usługę."""
    updated_service = crud.update_service(db, service_id=service_id, data=data)
    if updated_service is None:
        raise HTTPException(status_code=404, detail="Usługa nie znaleziona")
    return updated_service

@router.delete("/api/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_api(service_id: int, db: Session = Depends(get_db)):
    """Usuwa istniejącą usługę."""
    if not crud.delete_service(db, service_id=service_id):
        raise HTTPException(status_code=404, detail="Usługa nie znaleziona")
    return {"ok": True}

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
    try:
        # crud.create_service powinno dodać, zatwierdzić i odświeżyć model
        db_service = crud.create_service(
            db=db,
            service_type_id=service_data.service_type_id,
            date=service_data.date,
            price=service_data.base_price_net
        )
        return {
            "success": True,
            "service": {
                "id": db_service.id,
                "service_type_id": db_service.service_type_id,
                "date": db_service.date,
                "base_price_net": db_service.base_price_net
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# 2.1 Strona HTML z tabelą i modalem
@router.get("/services/add-type", response_class=HTMLResponse)
async def service_types_page(request: Request,
                             db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    vat_rates  = crud.get_vat_rates(db)
    return templates.TemplateResponse(
        "service_types.html",
        {
            "request": request,
            "categories": categories,
            "vat_rates": vat_rates,
            "page_title": "Typy usług"
        }
    )

# 2.2 API: lista typów
@router.get("/api/service_types", response_model=List[Dict[str, Any]])
async def get_service_types_api(db: Session = Depends(get_db)):
    service_types = crud.get_service_types(db)
    return [
        {
            "id": st.id,
            "name": st.name,
            "service_category_id": st.category_id,
            "vat_rate_id": st.vat_rate_id,
            "category": {
                "id": st.category.id,
                "name": st.category.name
            },
            "vat_rate": st.vat_rate.rate  # teraz zwracamy wartość VAT
        } for st in service_types
    ]

# 2.3 API: dodawanie nowego typu
@router.post("/api/service_types/add",
             response_model=schemas.ServiceTypeRecord,
             status_code=status.HTTP_201_CREATED)
async def add_service_type_api(data: schemas.ServiceTypeCreate,
                               db: Session = Depends(get_db)):
    try:
        st = crud.get_or_create_service_type(
            db=db,
            name=data.name,
            category_id=data.service_category_id,
            vat_rate_id=data.vat_rate_id
        )
        return {
            "id": st.id,
            "name": st.name,
            "service_category_id": st.category_id,
            "vat_rate_id": st.vat_rate_id,
            "category_name": st.category.name,
            "vat_rate": st.vat_rate.rate
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))

@router.put("/api/service_types/{type_id}", response_model=schemas.ServiceTypeRecord)
async def update_service_type_api(type_id: int,
                                  data: schemas.ServiceTypeCreate,
                                  db: Session = Depends(get_db)):
    """Aktualizuje istniejący typ usługi."""
    # W schemacie mamy service_category_id, a w modelu category_id - musimy to zmapować.
    # W tym przypadku przekazujemy cały obiekt `data` do funkcji CRUD.
    updated_type = crud.update_service_type(db, type_id=type_id, data=data)
    if not updated_type:
        raise HTTPException(status_code=404, detail="Typ usługi nie znaleziony")
    # Musimy ręcznie zbudować odpowiedź, aby pasowała do schematu
    return {
         "id": updated_type.id,
         "name": updated_type.name,
         "service_category_id": updated_type.category_id,
         "vat_rate_id": updated_type.vat_rate_id,
         "category_name": updated_type.category.name,
         "vat_rate": updated_type.vat_rate.rate
    }


@router.delete("/api/service_types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_type_api(type_id: int, db: Session = Depends(get_db)):
    """Usuwa istniejący typ usługi."""
    success = crud.delete_service_type(db, type_id=type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Typ usługi nie znaleziony")
    return {"ok": True}

# 1. Endpoint do wyświetlania strony HTML
@router.get("/services/add-category", response_class=HTMLResponse)
async def service_categories_page(request: Request, db: Session = Depends(get_db)):
    """Wyświetla stronę do zarządzania kategoriami usług."""
    return templates.TemplateResponse(
        "service_categories.html",
        {"request": request, "page_title": "Kategorie usług"}
    )

# 2. Endpoint API do pobierania listy kategorii w formacie JSON
@router.get("/api/service_categories", response_model=List[schemas.ServiceCategoryRecord])
async def get_service_categories_api(db: Session = Depends(get_db)):
    """Zwraca listę wszystkich kategorii usług."""
    return crud.get_categories(db)

# 3. Endpoint API do dodawania nowej kategorii
@router.post("/api/service_categories/add",
             response_model=schemas.ServiceCategoryRecord,
             status_code=status.HTTP_201_CREATED)
async def add_service_category_api(category_data: schemas.ServiceCategoryCreate,
                                   db: Session = Depends(get_db)):
    """Tworzy nową kategorię usługi."""
    # Sprawdzamy, czy kategoria o takiej nazwie już nie istnieje, aby uniknąć duplikatów
    existing_category = db.query(models.Category).filter(models.Category.name == category_data.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategoria o tej nazwie już istnieje"
        )
    return crud.get_or_create_category(db=db, name=category_data.name)

# 4. Endpoint API do aktualizacji kategorii (PUT)
@router.put("/api/service_categories/{category_id}", response_model=schemas.ServiceCategoryRecord)
async def update_service_category_api(category_id: int,
                                      category_data: schemas.ServiceCategoryCreate,
                                      db: Session = Depends(get_db)):
    """Aktualizuje istniejącą kategorię usługi."""
    updated_category = crud.update_category(db, category_id=category_id, name=category_data.name)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
    return updated_category

# 5. Endpoint API do usuwania kategorii (DELETE)
@router.delete("/api/service_categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_category_api(category_id: int, db: Session = Depends(get_db)):
    """Usuwa istniejącą kategorię usługi."""
    success = crud.delete_category(db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
    return {"ok": True} # Zwracamy pustą odpowiedź z kodem 204