from sqlalchemy.orm import Session
#from database import SessionLocal
from database_prod import SessionLocal

def get_db():
    if SessionLocal is None:
        raise Exception("Połączenie z bazą danych nie zostało zainicjowane.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()