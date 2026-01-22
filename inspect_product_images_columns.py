import pyodbc
from config import DB_CONNECTION


def main():
    print("Conectando...")
    conn = pyodbc.connect(DB_CONNECTION)
    cur = conn.cursor()

    cur.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'ProductImages'
        ORDER BY ORDINAL_POSITION
    """)

    print("Columns in dbo.ProductImages:")
    for (col,) in cur.fetchall():
        print(" -", col)

    conn.close()


if __name__ == "__main__":
    main()
