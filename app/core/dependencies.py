import os

if os.getenv("WEBSITE_SITE_NAME"): # Ta zmienna istnieje tylko na Azure
    from database_prod import SessionLocal
else: # W przeciwnym razie jesteśmy lokalnie
    from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()