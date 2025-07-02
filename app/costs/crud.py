import datetime
from sqlalchemy.orm import Session, joinedload
import app.costs.models as models

# --- Operacje CRUD dla Kontrahentów ---
def get_contractors(db: Session):
    return db.query(models.Contractor).all()

def get_or_create_contractor(db: Session, name: str):
    contractor = db.query(models.Contractor).filter(models.Contractor.name == name).first()
    if not contractor:
        contractor = models.Contractor(name=name)
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
    ).all()

def create_expense(
    db: Session,
    invoice_number: str,
    invoice_date: datetime.date,
    description: str,
    amount_net: float,
    amount_gross: float,
    currency: str,
    due_date: datetime.date,
    contractor_id: int,
    category_id: int,
    attachment_path: str = None
):
    db_expense = models.Expense(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        description=description,
        amount_net=amount_net,
        amount_gross=amount_gross,
        currency=currency,
        due_date=due_date,
        contractor_id=contractor_id,
        category_id=category_id,
        attachment_path=attachment_path
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def update_expense_payment_status(db: Session, expense_id: int, payment_date: datetime.date):
    expense = get_expense(db, expense_id)
    if expense:
        expense.payment_date = payment_date
        expense.is_paid = True
        db.commit()
        db.refresh(expense)
    return expense

def update_expense_accountant_status(db: Session, expense_id: int, transferred_date: datetime.date):
    expense = get_expense(db, expense_id)
    if expense:
        expense.transferred_to_accountant_date = transferred_date
        expense.is_transferred_to_accountant = True
        db.commit()
        db.refresh(expense)
    return expense

def delete_expense(db: Session, expense_id: int):
    expense = get_expense(db, expense_id)
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False