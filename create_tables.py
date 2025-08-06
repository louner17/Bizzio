# plik: create_tables.py
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

# Krok 1: Załaduj zmienne środowiskowe z pliku .env
print("Ładowanie zmiennych środowiskowych z pliku .env...")
load_dotenv()
print("Zmienne załadowane.")

# Krok 2: Zaimportuj Base z głównego pliku bazy danych
# Ważne, aby Base "wiedział" o wszystkich Twoich modelach
from database import Base
import app.services.models
import app.costs.models
import app.clients.models
import app.calendar.models

# Krok 3: Zbuduj połączenie z bazą PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Brak DATABASE_URL w pliku .env! Upewnij się, że plik istnieje i zawiera poprawne dane.")

engine = create_engine(DATABASE_URL)

# Krok 4: Stwórz wszystkie tabele
try:
    print(f"Łączenie z bazą danych i tworzenie tabel...")
    Base.metadata.create_all(bind=engine)
    print("--- SUKCES: Tabele zostały pomyślnie utworzone w bazie PostgreSQL! ---")
except Exception as e:
    print(f"\n--- BŁĄD: Wystąpił błąd podczas tworzenia tabel: {e} ---")