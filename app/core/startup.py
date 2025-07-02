import datetime
from sqlalchemy.orm import Session
from database import engine, SessionLocal

# Importujemy wszystkie modele, aby funkcja Base.metadata.create_all je wykryła
import app.services.models as services_models
import app.costs.models as costs_models

import app.services.crud as services_crud
import app.costs.crud as costs_crud

def run_startup_event():
    """Wypełnianie bazy danych danymi początkowymi przy starcie aplikacji."""
    db: Session = SessionLocal() # Używamy SessionLocal z database.py
    try:
        # Usuwamy wszystkie tabele (tylko w developmentie!)
        # Ta linia wymaga, aby Base miała dostęp do wszystkich modeli
        # Zapewniamy to poprzez zaimportowanie modules_models i costs_models powyżej.
        services_models.Base.metadata.drop_all(bind=engine)
        services_models.Base.metadata.create_all(bind=engine)

        # Upewnij się, że katalog na załączniki istnieje
        import os
        ATTACHMENTS_DIR = "attachments"
        os.makedirs(os.path.join(ATTACHMENTS_DIR, "expenses"), exist_ok=True)


        # Wypełnianie kategorii usług.
        w_cat = services_crud.get_or_create_category(db, name="Wizaż")
        r_cat = services_crud.get_or_create_category(db, name="Rzęsy")
        b_cat = services_crud.get_or_create_category(db, name="Brwi")
        p_cat = services_crud.get_or_create_category(db, name="Pakiet")

        # Wypełnianie polskich stawek VAT.
        vat_0 = services_crud.get_or_create_vat_rate(db, description="0%", rate=0.00)
        vat_5 = services_crud.get_or_create_vat_rate(db, description="5%", rate=0.05)
        vat_8 = services_crud.get_or_create_vat_rate(db, description="8%", rate=0.08)
        vat_23 = services_crud.get_or_create_vat_rate(db, description="23%", rate=0.23)

        # Wypełnianie typów usług.
        services_crud.get_or_create_service_type(db, name="Makijaż okolicznościowy", category_id=w_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Makijaż sesyjny", category_id=w_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Makijaż ślubny", category_id=w_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Makijaż próbny", category_id=w_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Rzęsy 1D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Uzupełnienie 1D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Rzęsy 2/3D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Uzupełnienie 2/3D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Rzęsy 4/5D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Uzupełnienie 4/5D", category_id=r_cat.id, vat_rate_id=vat_0.id)
        services_crud.get_or_create_service_type(db, name="Regulacja brwi", category_id=b_cat.id, vat_rate_id=vat_0.id)

        # --- Wypełnianie danych początkowych dla KOSZTÓW ---
        # Kategorie kosztów
        op_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Operacyjne", is_tax_deductible=True)
        mkt_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Marketingowe", is_tax_deductible=True)
        adm_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Administracyjne", is_tax_deductible=True)
        no_ded_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Niopodatkowe", is_tax_deductible=False)
        zus_cat = costs_crud.get_or_create_expense_category(db, name="ZUS", is_tax_deductible=True)

        # Kontrahenci
        google_c = costs_crud.get_or_create_contractor(db, name="Google Ireland Ltd.")
        office_c = costs_crud.get_or_create_contractor(db, name="Biuro Nieruchomości Sp. z o.o.")
        zus_c = costs_crud.get_or_create_contractor(db, name="Zakład Ubezpieczeń Społecznych")

        # Przykładowe koszty
        costs_crud.create_expense(
            db,
            invoice_number="FV/2025/01/001",
            invoice_date=datetime.date(2025, 1, 5),
            description="Reklama Google Ads",
            amount_net=150.00,
            amount_gross=184.50,
            currency="PLN",
            due_date=datetime.date(2025, 1, 19),
            contractor_id=google_c.id,
            category_id=mkt_cat.id
        )
        costs_crud.create_expense(
            db,
            invoice_number="FV/2025/01/002",
            invoice_date=datetime.date(2025, 1, 10),
            description="Czynsz za styczeń 2025",
            amount_net=2000.00,
            amount_gross=2460.00,
            currency="PLN",
            due_date=datetime.date(2025, 1, 15),
            contractor_id=office_c.id,
            category_id=op_cat.id
        )
        costs_crud.create_expense(
            db,
            invoice_number="ZUS/2025/01",
            invoice_date=datetime.date(2025, 1, 15),
            description="Składki ZUS za styczeń 2025",
            amount_net=0.00,
            amount_gross=1600.00,
            currency="PLN",
            due_date=datetime.date(2025, 1, 20),
            contractor_id=zus_c.id,
            category_id=zus_cat.id
        )
    finally:
        db.close()