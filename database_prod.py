# plik: database_prod.py (WERSJA OSTATECZNA)
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = None
SessionLocal = None
Base = declarative_base()


def connect_db():
    """Nawiązuje połączenie z bazą danych, ponawiając próbę w razie błędu."""
    global engine, SessionLocal

    retries = 5
    delay = 2  # sekundy

    for i in range(retries):
        try:
            print("--- [DEBUG] Próba połączenia z bazą danych... ---")
            db_user = os.environ["DB_USER"]
            db_pass = os.environ["DB_PASS"]
            db_name = os.environ["DB_NAME"]
            instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]

            print(f"--- [DEBUG] Używam INSTANCE_CONNECTION_NAME: {instance_connection_name}")

            SQLALCHEMY_DATABASE_URL = (
                f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
                f"?host=/cloudsql/{instance_connection_name}"
            )

            engine = create_engine(SQLALCHEMY_DATABASE_URL)

            # Testujemy połączenie
            with engine.connect() as connection:
                print("--- [DEBUG] Połączenie z bazą danych nawiązane pomyślnie! ---")

            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return  # Zakończ sukcesem

        except Exception as e:
            print(f"--- [DEBUG] Próba {i + 1}/{retries} nie powiodła się. Błąd: {e} ---")
            if i < retries - 1:
                print(f"--- [DEBUG] Ponawiam próbę za {delay}s... ---")
                time.sleep(delay)
            else:
                print("--- [BŁĄD KRYTYCZNY] Nie udało się połączyć z bazą danych po kilku próbach. ---")
                raise