import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_TRUSTED = (os.getenv("DB_TRUSTED", "no").lower() == "yes")

if not DB_SERVER or not DB_NAME:
    raise RuntimeError("Faltan DB_SERVER o DB_NAME en el .env")

if DB_TRUSTED:
    DB_CONNECTION = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    if not DB_USER or not DB_PASSWORD:
        raise RuntimeError(
            "Faltan DB_USER o DB_PASSWORD en el .env (y DB_TRUSTED=no)")

    DB_CONNECTION = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
