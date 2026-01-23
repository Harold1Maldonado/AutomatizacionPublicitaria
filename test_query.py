import pyodbc
from config import DB_CONNECTION


def main():
    conn = pyodbc.connect(DB_CONNECTION)
    cur = conn.cursor()

    #  1 fila de Products
    cur.execute(
        "SELECT TOP 1 product_id, featured, facebook_featured_at FROM Products")
    row = cur.fetchone()
    print("Products sample:", row)

    # 1 fila de ProductImages
    cur.execute(
        "SELECT TOP 1 product_id, img_sequence, img_url FROM ProductImages")
    row = cur.fetchone()
    print("ProductImages sample:", row)

    conn.close()


if __name__ == "__main__":
    main()
