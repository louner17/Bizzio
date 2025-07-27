
from fastapi import APIRouter, Request, Depends, Form, HTTPException, File, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_db
import app.costs.crud as crud
import app.costs.models as models
import app.costs.schemas as schemas

import fitz  # PyMuPDF
import re
import os

# WAŻNA ZMIANA: Usuwamy prefiks z definicji routera
router = APIRouter(tags=["Costs"])
templates = Jinja2Templates(directory="templates")
ATTACHMENTS_DIR = "attachments"

# --- ŚCIEŻKI DLA STRON HTML ---

@router.get("/costs/", response_class=HTMLResponse) # Pełna ścieżka
async def list_costs_page(request: Request, db: Session = Depends(get_db)):
    """Wyświetla główną stronę rejestru kosztów."""
    contractors = crud.get_contractors(db)
    expense_categories = crud.get_expense_categories(db)
    return templates.TemplateResponse("costs.html", {
        "request": request,
        "contractors": contractors,
        "expense_categories": expense_categories,
        "page_title": "Koszty"
    })

@router.get("/costs/add-category", response_class=HTMLResponse) # Pełna ścieżka
async def expense_categories_page(request: Request, db: Session = Depends(get_db)):
    """Wyświetla stronę do zarządzania kategoriami kosztów."""
    return templates.TemplateResponse(
        "expense_categories.html",
        {"request": request, "page_title": "Kategorie kosztów"}
    )

@router.get("/costs/api", response_model=List[schemas.Expense]) # Pełna ścieżka
async def get_expenses_api(db: Session = Depends(get_db)):
    """Zwraca listę wszystkich kosztów, posortowaną."""
    expenses = crud.get_expenses(db)
    return expenses

@router.post("/costs/api", response_model=schemas.Expense)
async def create_expense_api(
    db: Session = Depends(get_db),
    # Dane formularza odczytywane pojedynczo
    invoice_number: str = Form(...),
    invoice_date: date = Form(...),
    description: str = Form(...),
    amount_net: float = Form(...),
    amount_gross: float = Form(...),
    due_date: date = Form(...),
    contractor_name: str = Form(...),
    category_id: int = Form(...),
    is_paid: bool = Form(False),
    payment_date: Optional[date] = Form(None),
    attachment: Optional[UploadFile] = File(None)
):
    """Tworzy nowy koszt (fakturę) na podstawie danych z formularza."""
    expense_data = schemas.ExpenseCreate(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        description=description,
        amount_net=amount_net,
        amount_gross=amount_gross,
        due_date=due_date,
        contractor_name=contractor_name,
        category_id=category_id,
        is_paid=is_paid,
        payment_date=payment_date
    )
    return crud.create_expense(db=db, expense_data=expense_data, attachment=attachment)

@router.put("/costs/api/{expense_id}", response_model=schemas.Expense) # Pełna ścieżka
async def update_expense_api(expense_id: int, expense_data: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    updated = crud.update_expense(db, expense_id=expense_id, expense_data=expense_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Koszt nie znaleziony")
    return updated

@router.delete("/costs/api/{expense_id}", status_code=status.HTTP_204_NO_CONTENT) # Pełna ścieżka
async def delete_expense_api(expense_id: int, db: Session = Depends(get_db)):
    if not crud.delete_expense(db, expense_id=expense_id):
        raise HTTPException(status_code=404, detail="Koszt nie znaleziony")
    return {"ok": True}

@router.post("/costs/{expense_id}/pay") # Pełna ścieżka
async def pay_expense(expense_id: int, payment_date: date = Form(...), db: Session = Depends(get_db)):
    updated_expense = crud.update_expense_payment_status(db, expense_id, payment_date)
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Koszt nie znaleziony")
    return {"success": True, "message": "Koszt oznaczony jako opłacony."}

# --- ENDPOINTY API DLA KATEGORII KOSZTÓW ---

@router.get("/costs/api/categories", response_model=List[schemas.ExpenseCategory]) # Pełna ścieżka
async def get_expense_categories_api(db: Session = Depends(get_db)):
    return crud.get_expense_categories(db)

@router.post("/costs/api/categories", response_model=schemas.ExpenseCategory)
async def create_expense_category_api(
    category_data: schemas.ExpenseCategoryCreate,
    db: Session = Depends(get_db)
):
    return crud.get_or_create_expense_category(
        db,
        name=category_data.name,
        is_tax_deductible=category_data.is_tax_deductible
    )

# --- ENDPOINTY API DLA KONTRAHENTÓW ---
@router.get("/costs/api/contractors", response_model=List[schemas.Contractor]) # Pełna ścieżka
async def get_contractors_api(db: Session = Depends(get_db)):
    return crud.get_contractors(db)

@router.get("/costs/contractors", response_class=HTMLResponse)
async def contractors_page(request: Request, db: Session = Depends(get_db)):
    """Wyświetla stronę do zarządzania kontrahentami."""
    return templates.TemplateResponse(
        "contractors.html",
        {"request": request, "page_title": "Kontrahenci"}
    )


@router.post("/costs/api/contractors", response_model=schemas.Contractor)
async def create_contractor_api(
        contractor_data: schemas.ContractorCreate,
        db: Session = Depends(get_db)
):
    """Tworzy nowego kontrahenta."""
    existing = db.query(models.Contractor).filter(models.Contractor.name == contractor_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kontrahent o tej nazwie już istnieje."
        )

    return crud.get_or_create_contractor(
        db,
        name=contractor_data.name,
        bank_account_number=contractor_data.bank_account_number,
        is_recurring=contractor_data.is_recurring
    )

@router.put("/costs/api/contractors/{contractor_id}", response_model=schemas.Contractor)
async def update_contractor_api(
    contractor_id: int,
    contractor_data: schemas.ContractorCreate,
    db: Session = Depends(get_db)
):
    """Aktualizuje istniejącego kontrahenta."""
    updated_contractor = crud.update_contractor(db, contractor_id=contractor_id, contractor_data=contractor_data)
    if not updated_contractor:
        raise HTTPException(status_code=404, detail="Kontrahent nie znaleziony")
    return updated_contractor

@router.delete("/costs/api/contractors/{contractor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contractor_api(contractor_id: int, db: Session = Depends(get_db)):
    """Usuwa istniejącego kontrahenta."""
    success = crud.delete_contractor(db, contractor_id=contractor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kontrahent nie znaleziony")
    return {"ok": True}

@router.put("/costs/api/categories/{category_id}", response_model=schemas.ExpenseCategory)
async def update_expense_category_api(
    category_id: int,
    category_data: schemas.ExpenseCategory,
    db: Session = Depends(get_db)
):
    """Aktualizuje istniejącą kategorię kosztu."""
    updated = crud.update_expense_category(db, category_id=category_id, category_data=category_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
    return updated

@router.delete("/costs/api/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_category_api(category_id: int, db: Session = Depends(get_db)):
    """Usuwa istniejącą kategorię kosztu."""
    success = crud.delete_expense_category(db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
    return {"ok": True}

@router.post("/costs/api/export-for-accountant")
async def export_for_accountant(
    year: int = Form(...),
    month: int = Form(...),
    db: Session = Depends(get_db)
):
    """Tworzy paczkę ZIP z fakturami dla księgowego i zwraca ją do pobrania."""
    zip_buffer, zip_filename = crud.prepare_accountant_package(db, year=year, month=month)

    if not zip_buffer:
        raise HTTPException(status_code=404, detail="Nie znaleziono faktur do wygenerowania paczki dla podanego okresu.")

    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )