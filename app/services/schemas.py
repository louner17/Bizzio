# app/services/schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional


# --- KATEGORIE USŁUG ---
class ServiceCategoryBase(BaseModel):
    name: str


class ServiceCategoryCreate(ServiceCategoryBase):
    name: str

class ServiceCategoryRecord(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ServiceCategoryDisplay(ServiceCategoryBase):
    id: int

    class Config:
        orm_mode = True


# --- STAWKI VAT ---
class VatRateDisplay(BaseModel):
    id: int
    description: str
    rate: float

    class Config:
        orm_mode = True


# --- TYP USŁUGI ---
class ServiceTypeBase(BaseModel):
    name: str
    vat_rate_id: int
    service_category_id: int


class ServiceTypeCreate(BaseModel):
    name: str
    service_category_id: int
    vat_rate_id: int


# rekord zwracany w liście i po dodaniu
class ServiceTypeRecord(BaseModel):
    id: int
    name: str
    service_category_id: int
    vat_rate_id: int
    # dla wygody: nazwa kategorii i stawki VAT
    category_name: Optional[str]
    vat_rate: Optional[float]

    class Config:
        orm_mode = True

class ServiceTypeDisplay(ServiceTypeBase):
    id: int
    category: ServiceCategoryDisplay

    class Config:
        orm_mode = True


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

# rekord zwracany po utworzeniu – id + te same trzy pola
class ServiceRecord(BaseModel):
    id: int
    service_type_id: int
    date: date
    base_price_net: float

    class Config:
        orm_mode = True

# odpowiedź endpointu – flaga sukcesu + rekord
class ServiceDisplay(BaseModel):
    success: bool
    service: ServiceRecord