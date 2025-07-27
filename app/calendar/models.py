from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from app.clients.models import Client
from app.services.models import ServiceType


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(Enum("zaplanowana", "wykonana", "anulowana", name="appointment_status_enum"), default="zaplanowana")
    cancellation_reason = Column(String, nullable=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    service_type_id = Column(Integer, ForeignKey("service_type.id"))

    client = relationship("Client")
    service_type = relationship("ServiceType")