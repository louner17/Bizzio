from sqlalchemy import Column, Date, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base # Importujemy Base z database.py

# --- MODELE DLA KOSZTÓW ---

class Contractor(Base):
    __tablename__ = "contractors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    expenses = relationship("Expense", back_populates="contractor")

class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_tax_deductible = Column(Boolean, default=True)

    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    invoice_date = Column(Date, index=True)
    description = Column(String)
    amount_net = Column(Float)
    amount_gross = Column(Float)
    currency = Column(String, default="PLN")

    due_date = Column(Date)
    payment_date = Column(Date, nullable=True)
    is_paid = Column(Boolean, default=False)

    transferred_to_accountant_date = Column(Date, nullable=True)
    is_transferred_to_accountant = Column(Boolean, default=False)

    attachment_path = Column(String, nullable=True)

    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))

    contractor = relationship("Contractor", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")