# import datetime
# from sqlalchemy.orm import Session
# from database import engine, SessionLocal
#
# # Importujemy wszystkie modele, aby funkcja Base.metadata.create_all je wykryła
# import app.services.models as services_models
# import app.costs.models as costs_models
# import app.costs.schemas as costs_schemas
# import app.services.crud as services_crud
# import app.costs.crud as costs_crud
#
# def run_startup_event():
#     """Wypełnianie bazy danych danymi początkowymi przy starcie aplikacji."""
#     db: Session = SessionLocal() # Używamy SessionLocal z database.py
#     try:
#         # Usuwamy wszystkie tabele (tylko w developmentie!)
#         # Ta linia wymaga, aby Base miała dostęp do wszystkich modeli
#         # Zapewniamy to poprzez zaimportowanie modules_models i costs_models powyżej.
#         #services_models.Base.metadata.drop_all(bind=engine)
#         services_models.Base.metadata.create_all(bind=engine)
#
#         # Upewnij się, że katalog na załączniki istnieje
#         import os
#         ATTACHMENTS_DIR = "attachments"
#         os.makedirs(os.path.join(ATTACHMENTS_DIR, "expenses"), exist_ok=True)
#
#
#         # Wypełnianie kategorii usług.
#         w_cat = services_crud.get_or_create_category(db, name="Wizaż", color="#5D5FEF")
#         r_cat = services_crud.get_or_create_category(db, name="Rzęsy", color="#FF7A85")
#         b_cat = services_crud.get_or_create_category(db, name="Brwi", color="#4FD1C5")
#         p_cat = services_crud.get_or_create_category(db, name="Pakiet", color="#A0AEC0")
#
#         # Wypełnianie polskich stawek VAT.
#         vat_0 = services_crud.get_or_create_vat_rate(db, description="0%", rate=0.00)
#         vat_5 = services_crud.get_or_create_vat_rate(db, description="5%", rate=0.05)
#         vat_8 = services_crud.get_or_create_vat_rate(db, description="8%", rate=0.08)
#         vat_23 = services_crud.get_or_create_vat_rate(db, description="23%", rate=0.23)
#
#         # Wypełnianie typów usług.
#         services_crud.get_or_create_service_type(db, name="Makijaż okolicznościowy", category_id=w_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Makijaż sesyjny", category_id=w_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Makijaż ślubny", category_id=w_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Makijaż próbny", category_id=w_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Rzęsy 1D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Uzupełnienie 1D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Rzęsy 2/3D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Uzupełnienie 2/3D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Rzęsy 4/5D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Uzupełnienie 4/5D", category_id=r_cat.id, vat_rate_id=vat_0.id)
#         services_crud.get_or_create_service_type(db, name="Regulacja brwi", category_id=b_cat.id, vat_rate_id=vat_0.id)
#
#         # --- Wypełnianie danych początkowych dla KOSZTÓW ---
#         # Kategorie kosztów
#         op_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Operacyjne", is_tax_deductible=True)
#         mkt_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Marketingowe", is_tax_deductible=True)
#         adm_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Administracyjne", is_tax_deductible=True)
#         no_ded_cat = costs_crud.get_or_create_expense_category(db, name="Koszty Nieopodatkowe", is_tax_deductible=False)
#         zus_cat = costs_crud.get_or_create_expense_category(db, name="ZUS", is_tax_deductible=True)
#
#     finally:
#         db.close()


from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from database import SessionLocal

def run_startup_event():
    print("--- [DEBUG] Rozpoczynam skrypt startowy... ---")
    db: Session = None
    try:
        print("--- [DEBUG] Próba nawiązania sesji z bazą danych... ---")
        db = SessionLocal()
        print("--- [DEBUG] Sesja nawiązana. Próba wykonania prostego zapytania... ---")
        db.execute(text('SELECT 1'))
        print("--- [DEBUG] Połączenie z bazą danych SUKCES! ---")
    except Exception as e:
        print(f"--- [DEBUG] !!! BŁĄD POŁĄCZENIA Z BAZĄ DANYCH: {e} ---")
        raise
    finally:
        if db:
            db.close()
            print("--- [DEBUG] Sesja z bazą danych zamknięta. ---")