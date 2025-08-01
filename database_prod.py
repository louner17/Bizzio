# plik: database_prod.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Używamy oficjalnej metody połączenia z Cloud SQL Connector
from google.cloud.sql.connector import Connector, IPTypes

# Inicjalizacja connectora
connector = Connector()

# Funkcja do pobierania połączenia
def getconn():
    conn = connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"],
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        db=os.environ["DB_NAME"],
        ip_type=IPTypes.PRIVATE  # Użyj PRIVATE dla bezpieczniejszego połączenia
    )
    return conn

# Tworzymy silnik SQLAlchemy
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()