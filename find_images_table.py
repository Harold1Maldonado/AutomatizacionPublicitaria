import pyodbc
from config import DB_CONNECTION


def main():
    print("Arrancando find_images_table.py...")

    conn = pyodbc.connect(DB_CONNECTION)
    cur = conn.cursor()

    # 1) Buscar tablas que contengan "Image" en el nombre
    cur.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND TABLE_NAME LIKE '%Image%'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    rows = cur.fetchall()

    print(f"Tablas que contienen 'Image' en el nombre: {len(rows)}")
    for schema, name in rows:
        print(f" - {schema}.{name}")

    conn.close()


if __name__ == "__main__":
    main()
