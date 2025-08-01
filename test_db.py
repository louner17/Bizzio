# plik: test_db.py (TYLKO DO DEBUGOWANIA)
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

print("--- [DEBUG] Rozpoczynam skrypt testowy połączenia z bazą... ---")

try:
    # Krok 1: Odczyt zmiennych środowiskowych
    print("--- [DEBUG] Odczytuję zmienne środowiskowe...")
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    print("--- [DEBUG] Zmienne środowiskowe odczytane.")

    # Krok 2: Budowanie adresu URL
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
        f"?host=/cloudsql/{instance_connection_name}"
    )
    print("--- [DEBUG] Adres URL do bazy zbudowany.")

    # Krok 3: Tworzenie silnika SQLAlchemy
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("--- [DEBUG] Silnik SQLAlchemy stworzony.")

    # Krok 4: Testowe połączenie i zapytanie
    print("--- [DEBUG] Próba nawiązania połączenia i wykonania zapytania...")
    with SessionLocal() as db:
        db.execute(text('SELECT 1'))

    print("--- [SUKCES] Połączenie z bazą danych działa poprawnie! ---")

except Exception as e:
    print(f"--- [BŁĄD KRYTYCZNY] Połączenie z bazą danych NIE UDANE! ---")
    print(f"--- [SZCZEGÓŁY BŁĘDU] Typ: {type(e).__name__}, Wiadomość: {e} ---")
    # Rzucamy błąd ponownie, aby kontener na pewno się zatrzymał i zalogował błąd
    raise e
finally:
    # Dajemy logom chwilę na zapisanie się przed zakończeniem
    time.sleep(2)