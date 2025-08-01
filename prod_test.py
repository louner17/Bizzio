import os
import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector, IPTypes

# Tworzymy aplikację FastAPI
app = FastAPI()


# Definiujemy funkcję startową, która tylko łączy się z bazą
@app.on_event("startup")
def startup_event():
    print("--- [DIAGNOZA] Rozpoczynam event startowy...")
    try:
        # Ta sama logika połączenia, której używamy w aplikacji
        connector = Connector()

        def getconn():
            conn = connector.connect(
                os.environ["INSTANCE_CONNECTION_NAME"], "pg8000",
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASS"],
                db=os.environ["DB_NAME"],
                ip_type=IPTypes.PRIVATE
            )
            return conn

        engine = create_engine("postgresql+pg8000://", creator=getconn)

        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))

        print("--- [DIAGNOZA] SUKCES! Połączenie z bazą danych działa. ---")

    except Exception as e:
        print(f"--- [DIAGNOZA] KRYTYCZNY BŁĄD: {e} ---")
        # Rzucamy błąd, aby serwer na pewno się zatrzymał
        raise e


# Główny endpoint, który zobaczymy, jeśli aplikacja wystartuje
@app.get("/")
def read_root():
    return {"status": "Aplikacja testowa działa!"}