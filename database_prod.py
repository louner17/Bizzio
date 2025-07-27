# plik: database_prod.py (WERSJA OSTATECZNA)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Na razie tylko deklarujemy zmienne, nie tworzymy połączenia
engine = None
SessionLocal = None


def connect_to_db():
    """Tworzy połączenie z bazą danych na podstawie zmiennych środowiskowych."""
    global engine, SessionLocal

    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME")
    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

    if not all([db_user, db_pass, db_name, instance_connection_name]):
        raise ValueError("Brak wszystkich zmiennych środowiskowych do połączenia z bazą danych.")

    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
        f"?host=/cloudsql/{instance_connection_name}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()