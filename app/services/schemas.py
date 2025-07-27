# app/services/schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.clients.schemas import ClientInDB


# --- KATEGORIE USŁUG ---
class ServiceCategoryBase(BaseModel):
    name: str


class ServiceCategoryCreate(ServiceCategoryBase):
    name: str
    color: Optional[str] = '#A0AEC0'

class ServiceCategoryRecord(BaseModel):
    id: int
    name: str
    color: Optional[str] = '#A0AEC0'

    class Config:
        from_attributes = True


class ServiceCategoryDisplay(ServiceCategoryBase):
    id: int

    class Config:
        from_attributes = True


# --- STAWKI VAT ---
class VatRateDisplay(BaseModel):
    id: int
    description: str
    rate: float

    class Config:
        from_attributes = True


# --- TYP USŁUGI ---
class ServiceTypeBase(BaseModel):
    name: str
    vat_rate_id: int
    service_category_id: int


class ServiceTypeCreate(BaseModel):
    name: str
    service_category_id: int
    vat_rate_id: int
    default_price: Optional[float] = None
    duration_minutes: Optional[int] = 60


# rekord zwracany w liście i po dodaniu
class ServiceTypeRecord(BaseModel):
    id: int
    name: str
    service_category_id: int
    vat_rate_id: int
    category_name: Optional[str]
    vat_rate: Optional[float]
    default_price: Optional[float] = None
    duration_minutes: Optional[int] = 60

    class Config:
        from_attributes = True

class ServiceTypeDisplay(ServiceTypeBase):
    id: int
    category: ServiceCategoryDisplay

    class Config:
        from_attributes = True


# --- PODSTAWOWE SCHEMATY USŁUGI ---
class ServiceBase(BaseModel):
    service_type_id: int
    date: date
    base_price_net: float


class ServiceUpdateStatus(BaseModel):
    is_paid: Optional[bool] = None
    is_transferred_to_accountant: Optional[bool] = None


class ServiceCreate(BaseModel):
    service_type_id: int
    date: date
    base_price_net: float
    client_name: Optional[str] = None #

# rekord zwracany po utworzeniu – id + te same trzy pola
class ServiceRecord(BaseModel):
    id: int
    service_type_id: int
    date: date
    base_price_net: float

    class Config:
        from_attributes = True

# odpowiedź endpointu – flaga sukcesu + rekord
class ServiceDisplay(BaseModel):
    success: bool
    service: ServiceRecord
    new_client: Optional[ClientInDB] = None

class ClientInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    class Config:
        from_attributes = True

class ServiceSingleDisplay(ServiceRecord):
    client: Optional[ClientInfo] = None
    service_type: ServiceTypeRecord # Zakładając, że masz już ServiceTypeRecord