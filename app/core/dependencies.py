import os

if os.getenv("K_SERVICE"):
    from database_prod import get_session_local
else:
    from database import SessionLocal as local_SessionLocal

def get_db():
    Session = get_session_local() if os.getenv("K_SERVICE") else local_SessionLocal
    if Session is None:
        raise Exception("Połączenie z bazą danych nie zostało zainicjowane.")
    db = Session()
    try:
        yield db
    finally:
        db.close()