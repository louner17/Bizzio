import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Pobierz adres URL do bazy danych ze zmiennej środowiskowej
DATABASE_URL = os.getenv("DATABASE_URL")

# Jeśli aplikacja działa na serwerze (gdzie ustawimy DATABASE_URL), połącz się z PostgreSQL
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
# W przeciwnym razie (lokalnie), użyj pliku SQLite
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()