from database import SessionLocal

def get_db():
    if SessionLocal is None:
        raise Exception("Baza danych nie jest zainicjowana.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()