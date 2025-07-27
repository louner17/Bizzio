from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    source: Optional[str] = None
    birth_date: Optional[date] = None

    # --- NOWY WALIDATOR ---
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and (not v.isdigit() or len(v) > 9):
            raise ValueError('Numer telefonu może zawierać maksymalnie 9 cyfr.')
        return v

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    source: Optional[str] = None
    birth_date: Optional[date] = None

class ClientInDB(ClientBase):
    id: int
    date_added: date
    survey_path: Optional[str] = None
    class Config:
        from_attributes = True