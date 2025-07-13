from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class ContractorBase(BaseModel):
    name: str
    bank_account_number: Optional[str] = None
    is_recurring: Optional[bool] = False

class ContractorCreate(ContractorBase):
    pass

class Contractor(ContractorBase):
    id: int
    class Config:
        orm_mode = True

class ExpenseCategory(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class ExpenseBase(BaseModel):
    invoice_number: str
    invoice_date: date
    description: str
    amount_net: float
    amount_gross: float
    currency: str = "PLN"
    due_date: date
    category_id: int

class ExpenseCreate(ExpenseBase):
    # Pole do wpisania nazwy kontrahenta (nowego lub istniejącego)
    contractor_name: str
    is_paid: Optional[bool] = False
    payment_date: Optional[date] = None

class ExpenseUpdate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    is_paid: bool
    payment_date: Optional[date] = None
    is_transferred_to_accountant: bool
    transferred_to_accountant_date: Optional[date] = None
    attachment_path: Optional[str] = None
    contractor: Contractor
    category: ExpenseCategory
    # Dodajemy pole na kwotę VAT
    amount_vat: float

    class Config:
        orm_mode = True

class ExpenseCategoryCreate(BaseModel):
    name: str
    is_tax_deductible: bool = True

class ExpenseCategory(BaseModel):
    id: int
    name: str
    is_tax_deductible: bool = True # <-- DODAJ TĘ LINIĘ

    class Config:
        orm_mode = True