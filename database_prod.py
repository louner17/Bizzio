# plik: database_prod.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Połączenie "na sztywno" z bazą Cloud SQL przez Unix Socket
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
    f"?host=/cloudsql/{instance_connection_name}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()