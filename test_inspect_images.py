from config import DB_CONNECTION
import pyodbc
print("EJECUTANDO:", __file__)


def main():
    print("Conectando...")
    conn = pyodbc.connect(DB_CONNECTION)
    cur = conn.cursor()

    print("Buscando tablas con 'Image'...")
    cur.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND TABLE_NAME LIKE '%Image%'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    rows = cur.fetchall()

    print("Total:", len(rows))
    for schema, name in rows:
        print(f" - {schema}.{name}")

    conn.close()
    print("FIN.")


if __name__ == "__main__":
    main()
