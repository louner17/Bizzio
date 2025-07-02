import datetime
from sqlalchemy.orm import Session, joinedload
import app.services.models as models

# --- Operacje CRUD dla Usług ---
def get_services(db: Session):
    return db.query(models.Service).options(joinedload(models.Service.service_type)).all()

def create_service(db: Session, service_type_id: int, date: datetime.date, price: float):
    db_service = models.Service(
        service_type_id=service_type_id,
        date=date,
        base_price_net=price
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

# --- Operacje CRUD dla Kategorii ---
def get_categories(db: Session):
    return db.query(models.Category).all()

def get_or_create_category(db: Session, name: str):
    # Sprawdza, czy kategoria już istnieje.
    category = db.query(models.Category).filter(models.Category.name == name).first()
    # Jeśli nie, tworzy nową.
    if not category:
        category = models.Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
    return category

# --- Operacje CRUD dla Stawek VAT ---
def get_vat_rates(db: Session):
    return db.query(models.VatRate).all()

def get_or_create_vat_rate(db: Session, description: str, rate: float):
    # Sprawdza, czy stawka VAT już istnieje.
    vat_rate = db.query(models.VatRate).filter(models.VatRate.rate == rate).first()
    # Jeśli nie, tworzy nową.
    if not vat_rate:
        vat_rate = models.VatRate(description=description, rate=rate)
        db.add(vat_rate)
        db.commit()
        db.refresh(vat_rate)
    return vat_rate

# --- Operacje CRUD dla Typów Usług ---
def get_service_types(db: Session):
    return db.query(models.ServiceType).options(joinedload(models.ServiceType.category)).all()

def get_or_create_service_type(db: Session, name: str, category_id: int, vat_rate_id: int):
    # Sprawdza, czy usługa już istnieje.
    service_type = db.query(models.ServiceType).filter(models.ServiceType.name == name).first()
    # Jeśli nie, tworzy nową.
    if not service_type:
        service_type = models.ServiceType(name=name, category_id=category_id, vat_rate_id = vat_rate_id)
        db.add(service_type)
        db.commit()
        db.refresh(service_type)
    return service_type