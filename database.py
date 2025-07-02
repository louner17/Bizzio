from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Adres URL do naszej bazy danych SQLite. Plik "data.db" zostanie stworzony w głównym folderze.
SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"

# Tworzymy "silnik" bazy danych SQLAlchemy.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Tworzymy klasę SessionLocal, która będzie naszą sesją bazy danych.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Klasa bazowa, z której będą dziedziczyć nasze modele.
Base = declarative_base()