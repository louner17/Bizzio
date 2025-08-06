# plik: migrate_data.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Importuj wszystkie swoje modele, aby skrypt je znał
from app.services.models import Category as ServiceCategory, VatRate, ServiceType, Service
from app.costs.models import Contractor, ExpenseCategory, Expense
from app.clients.models import Client
from app.calendar.models import Appointment

print("--- Skrypt migracji danych z SQLite do PostgreSQL ---")
load_dotenv()

# --- ŹRÓDŁO: Lokalna baza danych SQLite ---
source_engine = create_engine("sqlite:///./data.db")
SourceSession = sessionmaker(bind=source_engine)

# --- CEL: Produkcyjna baza danych PostgreSQL ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Brak DATABASE_URL w pliku .env!")
target_engine = create_engine(DATABASE_URL)
TargetSession = sessionmaker(bind=target_engine)

# Kolejność migracji jest kluczowa, aby zachować relacje
MODELS_TO_MIGRATE = [
    ServiceCategory, VatRate, ExpenseCategory, Contractor, Client,
    ServiceType, Expense, Service, Appointment
]

source_session = SourceSession()
target_session = TargetSession()

try:
    print("Rozpoczynam migrację. To może potrwać chwilę...")
    for model in MODELS_TO_MIGRATE:
        table_name = model.__tablename__
        print(f"Migracja tabeli: {table_name}...")

        target_session.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;'))

        records = source_session.query(model).all()

        for record in records:
            new_record = model()
            for column in model.__table__.columns:
                setattr(new_record, column.name, getattr(record, column.name))
            target_session.add(new_record)

        target_session.commit()
        print(f"-> Sukces! Przeniesiono {len(records)} rekordów.")

    print("\n--- SUKCES: Migracja wszystkich danych zakończona! ---")

except Exception as e:
    print(f"\n--- BŁĄD: {e} ---")
    target_session.rollback()
finally:
    source_session.close()
    target_session.close()