import os

# Dynamicznie decydujemy, którego pliku bazy użyć
if os.getenv("K_SERVICE"): # Jeśli jesteśmy na Google Cloud
    from database_prod import SessionLocal
else: # Jeśli jesteśmy lokalnie
    from database import SessionLocal

def get_db():
    if SessionLocal is None:
        raise Exception("Połączenie z bazą danych nie zostało zainicjowane.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()