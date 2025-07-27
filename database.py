import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Sprawdź, czy aplikacja działa w środowisku Google Cloud Run
# GCP automatycznie ustawia tę zmienną środowiskową
if os.getenv("K_SERVICE"):
    # Połączenie z bazą Cloud SQL przez Unix Socket (najbezpieczniejsza metoda)
    db_user = os.environ["DB_USER"]      # np. postgres
    db_pass = os.environ["DB_PASS"]      # Hasło, które ustawisz w GCP
    db_name = os.environ["DB_NAME"]      # np. postgres
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"] # np. twoj-projekt:region:twoja-instancja

    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
        f"?host=/cloudsql/{instance_connection_name}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Jeśli działamy lokalnie, użyj pliku SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()