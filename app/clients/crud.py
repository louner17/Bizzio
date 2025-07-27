from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
import os
import shutil
from fastapi import UploadFile
from typing import Optional
from datetime import date
from . import models, schemas
from app.services.models import Service
from app.calendar.models import Appointment


def get_clients(db: Session, search: Optional[str] = None):
    """Pobiera listę klientów z opcjonalnym wyszukiwaniem i sortowaniem."""
    query = db.query(models.Client)
    if search:
        search_term = f"%{search}%"
        # Filtruj po imieniu LUB nazwisku, ignorując wielkość liter (ilike)
        query = query.filter(
            or_(
                models.Client.first_name.ilike(search_term),
                models.Client.last_name.ilike(search_term)
            )
        )
    return query.order_by(desc(models.Client.id)).all()


def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_client_by_details(db: Session, first_name: str, last_name: str, phone_number: Optional[str]):
    if not phone_number:
        return None
    return db.query(models.Client).filter(
        models.Client.first_name == first_name,
        models.Client.last_name == last_name,
        models.Client.phone_number == phone_number
    ).first()


def create_client(db: Session, client: schemas.ClientCreate, survey: Optional[UploadFile] = None):
    survey_path = None
    if survey and survey.filename:
        dir_path = os.path.join("attachments", "surveys")
        os.makedirs(dir_path, exist_ok=True)

        # Tworzenie unikalnej nazwy pliku ankiety
        survey_filename = f"ankieta_{client.first_name}_{client.last_name}_{date.today().isoformat()}.pdf"
        survey_path = os.path.join(dir_path, survey_filename)
        with open(survey_path, "wb+") as file_object:
            shutil.copyfileobj(survey.file, file_object)

    db_client = models.Client(
        **client.dict(),
        survey_path=survey_path
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client: schemas.ClientUpdate):
    """Aktualizuje dane istniejącego klienta."""
    db_client = get_client(db, client_id)
    if db_client:
        update_data = client.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int):
    client = get_client(db, client_id)
    if client:
        if client.survey_path and os.path.exists(client.survey_path):
            os.remove(client.survey_path)
        db.delete(client)
        db.commit()
        return True
    return False


def get_or_create_client_by_name(db: Session, full_name: str):
    if not full_name or not full_name.strip():
        return None, False

    # Dzielimy wpisaną frazę na części
    name_parts = [part for part in full_name.strip().lower().split() if part]

    # Budujemy dynamiczne zapytanie
    query = db.query(models.Client)
    # Każda część wpisanej frazy musi pasować do imienia lub nazwiska
    for part in name_parts:
        query = query.filter(
            or_(
                func.lower(models.Client.first_name).contains(part),
                func.lower(models.Client.last_name).contains(part)
            )
        )

    existing_client = query.first()

    if existing_client:
        # ZNALEZIONO ISTNIEJĄCEGO KLIENTA
        return existing_client, False

    # NIE ZNALEZIONO - TWORZYMY NOWEGO
    # Prosta logika do przypisania imienia i nazwiska
    first_name = name_parts[0].capitalize() if name_parts else ""
    last_name = " ".join(p.capitalize() for p in name_parts[1:]) if len(name_parts) > 1 else ""

    new_client_data = schemas.ClientCreate(first_name=first_name, last_name=last_name)
    new_client = create_client(db, client=new_client_data)
    return new_client, True


def get_last_service_for_client(db: Session, client_id: int):
    """Znajduje najnowszą usługę lub wizytę dla klienta i zwraca ID typu usługi."""

    # Znajdź ostatnią wykonaną usługę
    last_service = db.query(Service).filter(Service.client_id == client_id).order_by(desc(Service.date)).first()

    # Znajdź ostatnią zaplanowaną wizytę
    last_appointment = db.query(Appointment).filter(Appointment.client_id == client_id).order_by(
        desc(Appointment.start_time)).first()

    last_service_date = last_service.date if last_service else None
    last_appointment_date = last_appointment.start_time.date() if last_appointment else None

    # Porównaj daty i zwróć ID typu usługi z nowszego rekordu
    if last_service_date and (not last_appointment_date or last_service_date >= last_appointment_date):
        return last_service.service_type_id
    elif last_appointment_date:
        return last_appointment.service_type_id

    return None