import pyodbc
from config import DB_CONNECTION


def main():
    conn = pyodbc.connect(DB_CONNECTION, timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("DB OK ->", cur.fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()
