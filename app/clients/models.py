from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql import func
from database import Base

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    phone_number = Column(String, nullable=True)
    source = Column(String, nullable=True) # Źródło pozyskania
    birth_date = Column(Date, nullable=True)
    survey_path = Column(String, nullable=True) # Ścieżka do skanu ankiety
    date_added = Column(Date, default=func.current_date())