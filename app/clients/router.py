from fastapi import APIRouter, Request, Depends, File, UploadFile, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.dependencies import get_db
from . import crud, schemas

router = APIRouter(tags=["Clients"])
templates = Jinja2Templates(directory="templates")

@router.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request, "page_title": "Klienci"})

@router.get("/clients/api", response_model=List[schemas.ClientInDB])
async def get_clients_api(db: Session = Depends(get_db), search: Optional[str] = None):
    return crud.get_clients(db, search=search)


@router.post("/clients/api", response_model=schemas.ClientInDB)
async def create_client_api(
        first_name: str = Form(...),
        last_name: str = Form(...),
        phone_number: Optional[str] = Form(None),
        source: Optional[str] = Form(None),
        birth_date: Optional[date] = Form(None),
        survey: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    # --- NOWA LOGIKA WALIDACJI ---
    existing_client = crud.get_client_by_details(
        db, first_name=first_name, last_name=last_name, phone_number=phone_number
    )
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Klient o takim imieniu, nazwisku i numerze telefonu już istnieje."
        )

    # Jeśli nie ma duplikatu, kontynuujemy tworzenie klienta
    client_data = schemas.ClientCreate(
        first_name=first_name, last_name=last_name,
        phone_number=phone_number, source=source, birth_date=birth_date
    )
    return crud.create_client(db=db, client=client_data, survey=survey)

@router.delete("/clients/api/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_api(client_id: int, db: Session = Depends(get_db)):
    if not crud.delete_client(db, client_id):
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return {"ok": True}

@router.get("/clients/api/{client_id}", response_model=schemas.ClientInDB)
async def get_client_api(client_id: int, db: Session = Depends(get_db)):
    """Pobiera dane pojedynczego klienta."""
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return db_client

@router.put("/clients/api/{client_id}", response_model=schemas.ClientInDB)
async def update_client_api(
    client_id: int,
    client_data: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    """Aktualizuje dane klienta."""
    updated_client = crud.update_client(db, client_id=client_id, client=client_data)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return updated_client

@router.get("/clients/api/{client_id}/last-service")
async def get_client_last_service_api(client_id: int, db: Session = Depends(get_db)):
    """Zwraca ID ostatniego typu usługi dla danego klienta."""
    last_service_type_id = crud.get_last_service_for_client(db, client_id=client_id)
    return {"last_service_type_id": last_service_type_id}