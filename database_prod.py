# plik: database_prod.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None
SessionLocal = None

def get_engine():
    global engine
    if engine is None:
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
        instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")

        if not all([db_user, db_pass, db_name, instance_connection_name]):
            raise ValueError("Brak wszystkich zmiennych środowiskowych do połączenia z bazą.")

        SQLALCHEMY_DATABASE_URL = (
            f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
            f"?host=/cloudsql/{instance_connection_name}"
        )
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine

def get_session_local():
    global SessionLocal
    if SessionLocal is None:
        eng = get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return SessionLocal