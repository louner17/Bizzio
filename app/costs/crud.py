import datetime
import io
import zipfile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, extract
import app.costs.models as models
import app.costs.schemas as schemas
import os
import shutil
from fastapi import UploadFile
from typing import Optional

# --- Operacje CRUD dla Kontrahentów ---
def get_contractors(db: Session):
    return db.query(models.Contractor).all()

def get_or_create_contractor(db: Session, name: str, bank_account_number: Optional[str] = None, is_recurring: bool = False):
    contractor = db.query(models.Contractor).filter(models.Contractor.name == name).first()
    if not contractor:
        contractor = models.Contractor(
            name=name,
            bank_account_number=bank_account_number,
            is_recurring=is_recurring
        )
        db.add(contractor)
        db.commit()
        db.refresh(contractor)
    return contractor

# --- Operacje CRUD dla Kategorii Kosztów ---
def get_expense_categories(db: Session):
    return db.query(models.ExpenseCategory).all()

def get_or_create_expense_category(db: Session, name: str, is_tax_deductible: bool = True):
    category = db.query(models.ExpenseCategory).filter(models.ExpenseCategory.name == name).first()
    if not category:
        category = models.ExpenseCategory(name=name, is_tax_deductible=is_tax_deductible)
        db.add(category)
        db.commit()
        db.refresh(category)
    return category

# --- Operacje CRUD dla Kosztów ---
def get_expenses(db: Session):
    return db.query(models.Expense).options(
        joinedload(models.Expense.contractor),
        joinedload(models.Expense.category)
    ).order_by(desc(models.Expense.invoice_date)).all()


def create_expense(db: Session, expense_data: schemas.ExpenseCreate, attachment: Optional[UploadFile] = None):
    # Logika "znajdź lub stwórz" dla kontrahenta
    contractor = get_or_create_contractor(db, name=expense_data.contractor_name)
    attachment_path = None
    if attachment and attachment.filename:
        # Tworzenie ścieżki na podstawie daty faktury: attachments/expenses/MM_YYYY/
        invoice_date = expense_data.invoice_date
        dir_path = os.path.join("attachments", "expenses", f"{invoice_date.month:02d}_{invoice_date.year}")
        os.makedirs(dir_path, exist_ok=True)

        # Zapisanie pliku
        attachment_path = os.path.join(dir_path, attachment.filename)
        with open(attachment_path, "wb+") as file_object:
            shutil.copyfileobj(attachment.file, file_object)

    db_expense = models.Expense(
        invoice_number=expense_data.invoice_number,
        invoice_date=expense_data.invoice_date,
        description=expense_data.description,
        amount_net=expense_data.amount_net,
        amount_gross=expense_data.amount_gross,
        currency=expense_data.currency,
        due_date=expense_data.due_date,
        contractor_id=contractor.id,
        category_id=expense_data.category_id,
        attachment_path=attachment_path,
        is_paid=expense_data.is_paid or False,
        payment_date=expense_data.payment_date if expense_data.is_paid else None,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def update_expense(db: Session, expense_id: int, expense_data: schemas.ExpenseUpdate):
    db_expense = get_expense(db, expense_id)
    if db_expense:
        # Aktualizacja pól
        for var, value in vars(expense_data).items():
            setattr(db_expense, var, value) if value else None
        db.commit()
        db.refresh(db_expense)
    return db_expense

def update_expense_payment_status(db: Session, expense_id: int, payment_date: datetime.date):
    """Oznacza koszt jako opłacony w danym dniu."""
    expense = get_expense(db, expense_id) # Używamy istniejącej funkcji get_expense
    if expense:
        expense.is_paid = True
        expense.payment_date = payment_date
        db.commit()
        db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int):
    """Usuwa koszt oraz powiązany z nim załącznik z dysku."""
    expense = get_expense(db, expense_id)
    if expense:
        # Jeśli istnieje ścieżka do załącznika i plik istnieje, usuń go
        if expense.attachment_path and os.path.exists(expense.attachment_path):
            os.remove(expense.attachment_path)

        db.delete(expense)
        db.commit()
        return True
    return False

def update_contractor(db: Session, contractor_id: int, contractor_data: schemas.ContractorCreate):
    """Aktualizuje dane istniejącego kontrahenta."""
    db_contractor = db.query(models.Contractor).filter(models.Contractor.id == contractor_id).first()
    if db_contractor:
        db_contractor.name = contractor_data.name
        db_contractor.bank_account_number = contractor_data.bank_account_number
        db_contractor.is_recurring = contractor_data.is_recurring
        db.commit()
        db.refresh(db_contractor)
    return db_contractor

def delete_contractor(db: Session, contractor_id: int):
    """Usuwa kontrahenta o podanym ID."""
    db_contractor = db.query(models.Contractor).filter(models.Contractor.id == contractor_id).first()
    if db_contractor:
        db.delete(db_contractor)
        db.commit()
        return True
    return False

def update_expense_category(db: Session, category_id: int, category_data: schemas.ExpenseCategory):
    """Aktualizuje kategorię kosztu."""
    db_category = db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id).first()
    if db_category:
        db_category.name = category_data.name
        # --- DODANA LINIA DO AKTUALIZACJI STANU CHECKBOXA ---
        db_category.is_tax_deductible = category_data.is_tax_deductible
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_expense_category(db: Session, category_id: int):
    """Usuwa kategorię kosztu."""
    db_category = db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


def prepare_accountant_package(db: Session, year: int, month: int):
    """
    Zbiera podatkowe faktury kosztowe z danego miesiąca, pakuje załączniki do ZIP
    i aktualizuje status rekordów w bazie danych.
    """
    # 1. Znajdź wszystkie koszty podatkowe z danego okresu, które mają załącznik
    costs_to_process = db.query(models.Expense).options(
        joinedload(models.Expense.category),
        joinedload(models.Expense.contractor)
    ).filter(
        models.Expense.attachment_path.isnot(None),
        models.Expense.category.has(is_tax_deductible=True),
        extract('year', models.Expense.invoice_date) == year,
        extract('month', models.Expense.invoice_date) == month
    ).all()

    if not costs_to_process:
        return None, None  # Nie znaleziono faktur do przetworzenia

    # 2. Stwórz archiwum ZIP w pamięci
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for cost in costs_to_process:
            if os.path.exists(cost.attachment_path):
                # 3. Stwórz nową, ustandaryzowaną nazwę pliku
                contractor_name = cost.contractor.name.replace(' ', '_').lower()
                invoice_month = f"{cost.invoice_date.month:02d}"
                invoice_year = cost.invoice_date.year
                _, file_extension = os.path.splitext(cost.attachment_path)
                new_filename = f"fv_{contractor_name}_{invoice_month}_{invoice_year}{file_extension}"

                # 4. Dodaj plik do ZIP-a pod nową nazwą
                zip_file.write(cost.attachment_path, arcname=new_filename)

    # 5. Zaktualizuj status przetworzonych kosztów w bazie danych
    for cost in costs_to_process:
        cost.is_transferred_to_accountant = True
        cost.transferred_to_accountant_date = datetime.date.today()

    db.commit()

    # Przygotuj nazwę pliku ZIP do pobrania
    zip_filename = f"pawlowska_atelier_ksiegowosc_{month:02d}_{year}.zip"

    # Przewiń bufor na początek, aby można go było odczytać
    zip_buffer.seek(0)

    return zip_buffer, zip_filename