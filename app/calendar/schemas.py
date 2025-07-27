# plik: app/calendar/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.clients.schemas import ClientInDB

class AppointmentBase(BaseModel):
    start: datetime
    end: datetime
    title: str # Będzie zawierać np. "Anna Kowalska - Rzęsy 2D"
    service_type_id: int
    client_name: str # Przyjmujemy nazwę, backend zajmie się resztą
    price: float
    description: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    title: Optional[str] = None
    service_type_id: Optional[int] = None
    client_name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class AppointmentCreateResponse(BaseModel):
    success: bool
    appointment: dict # Prosty słownik z danymi wizyty
    new_client: Optional[ClientInDB] = None