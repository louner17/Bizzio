from sqlalchemy import Column, Date ,Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    service_types = relationship("ServiceType", back_populates="category")

class VatRate(Base):
    __tablename__ = "vat_rates"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, unique=True) # np. "23%"
    rate = Column(Float, unique=True) # np. 0.23

    service_types = relationship("ServiceType", back_populates="vat_rate")

class ServiceType(Base):
    __tablename__ = "service_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    vat_rate_id = Column(Integer, ForeignKey("vat_rates.id"))

    vat_rate = relationship("VatRate", back_populates="service_types")
    category = relationship("Category", back_populates="service_types")
    services = relationship("Service", back_populates="service_type")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    base_price_net = Column(Float)
    service_type_id = Column(Integer, ForeignKey("service_type.id"))

    service_type = relationship("ServiceType", back_populates="services")