import pyodbc
from config import DB_CONNECTION


def main():
    conn = pyodbc.connect(DB_CONNECTION)
    cur = conn.cursor()

    cur.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Products'
        ORDER BY ORDINAL_POSITION
    """)
    cols = [r[0] for r in cur.fetchall()]
    print("Columns in Products:")
    for c in cols:
        print(" -", c)

    conn.close()


if __name__ == "__main__":
    main()
