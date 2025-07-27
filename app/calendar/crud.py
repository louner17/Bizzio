# plik: app/calendar/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from datetime import datetime
from . import models, schemas
from app.clients import crud as clients_crud
from app.services.schemas import ServiceCreate
from app.services import crud as services_crud
from typing import Optional
import pytz

def get_appointments(db: Session, start: datetime, end: datetime):
    start_naive = start.replace(tzinfo=None)
    end_naive = end.replace(tzinfo=None)
    return db.query(models.Appointment).options(
        joinedload(models.Appointment.client),
        joinedload(models.Appointment.service_type).joinedload(models.ServiceType.category)
    ).filter(
        models.Appointment.start_time < end_naive,
        models.Appointment.end_time > start_naive,
        models.Appointment.status != 'anulowana'
    ).all()


def create_appointment(db: Session, appointment_data: schemas.AppointmentCreate):
    client, was_created = clients_crud.get_or_create_client_by_name(db, full_name=appointment_data.client_name)

    db_appointment = models.Appointment(
        start_time=appointment_data.start,
        end_time=appointment_data.end,
        description=appointment_data.description,
        price=appointment_data.price,
        client_id=client.id,
        service_type_id=appointment_data.service_type_id
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment, client if was_created else None


def update_appointment_time(db: Session, appointment_id: int, start: datetime, end: datetime):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.start_time = start
        db_appointment.end_time = end
        db.commit()
        db.refresh(db_appointment)
    return db_appointment


def update_appointment(db: Session, appointment_id: int, appointment_data: schemas.AppointmentUpdate):
    """Aktualizuje dane wizyty na podstawie pól dostarczonych w żądaniu."""
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not db_appointment:
        return None

    # Pobierz tylko te dane, które zostały jawnie przesłane w żądaniu
    update_data = appointment_data.dict(exclude_unset=True)

    # Aktualizuj klienta, jeśli podano nową nazwę
    if "client_name" in update_data:
        client, _ = clients_crud.get_or_create_client_by_name(db, full_name=update_data["client_name"])
        db_appointment.client_id = client.id

    # Zaktualizuj pozostałe pola, jeśli istnieją w przesłanych danych
    for key, value in update_data.items():
        # Pomijamy 'client_name', bo obsłużyliśmy go osobno
        if key != "client_name":
            # Mapujemy nazwy pól ze schematu na nazwy kolumn w modelu
            if key == "start":
                setattr(db_appointment, "start_time", value)
            elif key == "end":
                setattr(db_appointment, "end_time", value)
            else:
                setattr(db_appointment, key, value)

    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def mark_appointment_as_completed(db: Session, appointment_id: int):
    """Zmienia status wizyty na 'wykonana' i tworzy wpis w Rejestrze Usług."""
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment and db_appointment.status != 'wykonana':
        # 1. Zmień status wizyty
        db_appointment.status = 'wykonana'

        # 2. Przygotuj dane do stworzenia nowej usługi
        service_data = ServiceCreate(
            service_type_id=db_appointment.service_type_id,
            date=db_appointment.start_time.date(), # Używamy daty z wizyty
            base_price_net=db_appointment.price,
            client_name=f"{db_appointment.client.first_name} {db_appointment.client.last_name}"
        )

        # 3. Stwórz wpis w usługach
        services_crud.create_service(db, service_data=service_data)

        db.commit()
        db.refresh(db_appointment)
    return db_appointment


def check_for_overlap(db: Session, start_time: datetime, end_time: datetime, appointment_id: Optional[int] = None):
    """Sprawdza, czy w danym przedziale czasowym istnieje już inna wizyta."""
    query = db.query(models.Appointment).filter(
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > start_time,
        models.Appointment.status != 'anulowana'
    )
    # Przy edycji wykluczamy sprawdzaną wizytę
    if appointment_id:
        query = query.filter(models.Appointment.id != appointment_id)

    return query.first() is not None

def cancel_appointment(db: Session, appointment_id: int, reason: str):
    """Zmienia status wizyty na 'anulowana' i zapisuje powód."""
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = 'anulowana'
        db_appointment.cancellation_reason = reason
        db.commit()
        db.refresh(db_appointment)
    return db_appointment