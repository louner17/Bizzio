import datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc # Importujemy desc do sortowania
import app.services.models as models
import app.services.schemas as schemas

# --- Operacje CRUD dla Usług ---
def get_services(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None):
    """Pobiera usługi, z opcjonalnym filtrowaniem po dacie i sortowaniem malejąco."""
    query = db.query(models.Service).options(
        joinedload(models.Service.service_type).joinedload(models.ServiceType.category),
        joinedload(models.Service.service_type).joinedload(models.ServiceType.vat_rate)
    )
    if start_date:
        query = query.filter(models.Service.date >= start_date)
    if end_date:
        query = query.filter(models.Service.date <= end_date)

    # Sortowanie od najnowszej do najstarszej
    return query.order_by(desc(models.Service.date)).all()

def create_service(db: Session, service_type_id: int, date: datetime.date, price: float):
    db_service = models.Service(
        service_type_id=service_type_id,
        date=date,
        base_price_net=price
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    loaded_service = db.query(models.Service).options(
        joinedload(models.Service.service_type).joinedload(models.ServiceType.category)
    ).filter(models.Service.id == db_service.id).first()

    # Critical check:
    if not loaded_service.service_type:
        raise ValueError(f"ServiceType not loaded for service ID {loaded_service.id}")
    if not loaded_service.service_type.category:
        raise ValueError(f"ServiceCategory not loaded for ServiceType ID {loaded_service.service_type.id}")

    return loaded_service

def get_service(db: Session, service_id: int):
    """Pobiera pojedynczą usługę o danym ID."""
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def update_service(db: Session, service_id: int, data: schemas.ServiceCreate):
    """Aktualizuje istniejącą usługę."""
    db_service = get_service(db, service_id)
    if db_service:
        db_service.service_type_id = data.service_type_id
        db_service.date = data.date
        db_service.base_price_net = data.base_price_net
        db.commit()
        db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int):
    """Usuwa usługę o podanym ID."""
    db_service = get_service(db, service_id)
    if db_service:
        db.delete(db_service)
        db.commit()
        return True
    return False

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
    return db.query(models.ServiceType).options(
        joinedload(models.ServiceType.category),
        joinedload(models.ServiceType.vat_rate)
    ).all()

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

def update_service_type(db: Session, type_id: int, data: models.ServiceType):
    """Aktualizuje istniejący typ usługi."""
    db_type = db.query(models.ServiceType).filter(models.ServiceType.id == type_id).first()
    if db_type:
        db_type.name = data.name
        db_type.category_id = data.service_category_id
        db_type.vat_rate_id = data.vat_rate_id
        db.commit()
        db.refresh(db_type)
    return db_type

def delete_service_type(db: Session, type_id: int):
    """Usuwa typ usługi o podanym ID."""
    db_type = db.query(models.ServiceType).filter(models.ServiceType.id == type_id).first()
    if db_type:
        db.delete(db_type)
        db.commit()
        return True
    return False

def update_category(db: Session, category_id: int, name: str):
    """Aktualizuje nazwę istniejącej kategorii."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db_category.name = name
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    """Usuwa kategorię o podanym ID."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False