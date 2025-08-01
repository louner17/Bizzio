import os

# Dynamicznie decydujemy, którego pliku bazy użyć
if os.getenv("K_SERVICE"):
    from database_prod import SessionLocal
else:
    from database import SessionLocal

def get_db():
    if SessionLocal is None:
        raise Exception("Aplikacja nie jest połączona z bazą danych.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()