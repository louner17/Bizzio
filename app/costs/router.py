from fastapi import APIRouter, Request, Depends, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import datetime
import os
import shutil

# Importujemy zależności z naszego nowego modułu core
from app.core.dependencies import get_db

# Importujemy CRUD i modele z bieżącego modułu costs
import app.costs.crud as crud
import app.costs.models as models # Możesz nie potrzebować bezpośrednio, ale dobra praktyka by mieć


router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Ustawienia dla załączników
ATTACHMENTS_DIR = "attachments"

@router.get("/costs", response_class=HTMLResponse)
async def list_costs(request: Request, db: Session = Depends(get_db)):
    """Wyświetla listę wszystkich kosztów oraz formularze do zarządzania kosztami."""
    contractors = crud.get_contractors(db)
    expense_categories = crud.get_expense_categories(db)
    initial_date = datetime.date.today().strftime('%Y-%m-%d')
    return templates.TemplateResponse("costs.html", {
        "request": request,
        "contractors": contractors,
        "expense_categories": expense_categories,
        "initial_date": initial_date,
        "page_title": "Koszty"
    })

@router.get("/api/expenses", response_model=List[Dict[str, Any]])
async def get_expenses_api(db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db)
    return [
        {
            "id": e.id,
            "invoice_number": e.invoice_number,
            "invoice_date": e.invoice_date.isoformat(),
            "description": e.description,
            "amount_net": e.amount_net,
            "amount_gross": e.amount_gross,
            "currency": e.currency,
            "due_date": e.due_date.isoformat(),
            "payment_date": e.payment_date.isoformat() if e.payment_date else None,
            "is_paid": e.is_paid,
            "transferred_to_accountant_date": e.transferred_to_accountant_date.isoformat() if e.transferred_to_accountant_date else None,
            "is_transferred_to_accountant": e.is_transferred_to_accountant,
            "attachment_path": e.attachment_path,
            "contractor": {
                "id": e.contractor.id,
                "name": e.contractor.name
            },
            "category": {
                "id": e.category.id,
                "name": e.category.name,
                "is_tax_deductible": e.category.is_tax_deductible
            }
        } for e in expenses
    ]

@router.get("/api/contractors", response_model=List[Dict[str, Any]])
async def get_contractors_api(db: Session = Depends(get_db)):
    contractors = crud.get_contractors(db)
    return [
        {
            "id": c.id,
            "name": c.name
        } for c in contractors
    ]

@router.get("/api/expense_categories", response_model=List[Dict[str, Any]])
async def get_expense_categories_api(db: Session = Depends(get_db)):
    expense_categories = crud.get_expense_categories(db)
    return [
        {
            "id": ec.id,
            "name": ec.name,
            "is_tax_deductible": ec.is_tax_deductible
        } for ec in expense_categories
    ]

@router.post("/costs/add", response_class=RedirectResponse)
async def add_expense(
        invoice_number: str = Form(...),
        invoice_date: datetime.date = Form(...),
        description: str = Form(...),
        amount_net: float = Form(...),
        amount_gross: float = Form(...),
        currency: str = Form("PLN"),
        due_date: datetime.date = Form(...),
        contractor_name: str = Form(...),
        category_id: int = Form(...),
        attachment: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    contractor = crud.get_or_create_contractor(db, name=contractor_name)

    attachment_path = None
    if attachment and attachment.filename:
        # Tworzenie ścieżki do zapisu pliku: attachments/expenses/YYYY/MM/filename.ext
        year_month_path = os.path.join(ATTACHMENTS_DIR, "expenses",
                                      str(invoice_date.year),
                                      str(invoice_date.month).zfill(2))
        os.makedirs(year_month_path, exist_ok=True)
        file_location = os.path.join(year_month_path, attachment.filename)

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(attachment.file, file_object)
        attachment_path = file_location

    crud.create_expense(
        db=db,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        description=description,
        amount_net=amount_net,
        amount_gross=amount_gross,
        currency=currency,
        due_date=due_date,
        contractor_id=contractor.id,
        category_id=category_id,
        attachment_path=attachment_path
    )
    return RedirectResponse(url="/costs", status_code=303)

@router.post("/costs/{expense_id}/pay", response_class=JSONResponse)
async def pay_expense(expense_id: int, request: Request, db: Session = Depends(get_db)):
    payment_date = datetime.date.today()
    updated_expense = crud.update_expense_payment_status(db, expense_id, payment_date)
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense marked as paid", "payment_date": payment_date.isoformat()}

@router.post("/costs/{expense_id}/to_accountant", response_class=JSONResponse)
async def transfer_expense_to_accountant(expense_id: int, request: Request, db: Session = Depends(get_db)):
    transferred_date = datetime.date.today()
    updated_expense = crud.update_expense_accountant_status(db, expense_id, transferred_date)
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense marked as transferred to accountant", "transferred_date": transferred_date.isoformat()}

@router.post("/contractors/add", response_class=RedirectResponse)
async def add_contractor_from_form(name: str = Form(...), db: Session = Depends(get_db)):
    crud.get_or_create_contractor(db, name=name)
    return RedirectResponse(url="/costs", status_code=303)

@router.post("/expense_categories/add", response_class=RedirectResponse)
async def add_expense_category_from_form(
        name: str = Form(...),
        is_tax_deductible: bool = Form(True),
        db: Session = Depends(get_db)
):
    crud.get_or_create_expense_category(db, name=name, is_tax_deductible=is_tax_deductible)
    return RedirectResponse(url="/costs", status_code=303)