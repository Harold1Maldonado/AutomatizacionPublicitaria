import pyodbc
from config import DB_CONNECTION


class DandyDealsDB:
    def __init__(self):
        self.conn = pyodbc.connect(DB_CONNECTION)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_next_featured_for_facebook(self):
        query = """
        SELECT TOP 1
            p.product_id,
            p.product,
            i.img_url
        FROM dbo.Products p
        OUTER APPLY (
            SELECT TOP 1 img_url
            FROM dbo.ProductImages
            WHERE product_id = p.product_id
            ORDER BY img_sequence ASC, id ASC
        ) i
        WHERE
            p.featured = 1
            AND p.facebook_featured_at IS NULL
            AND i.img_url IS NOT NULL
        ORDER BY p.date_added_to_sheet ASC;
        """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if not row:
            return None

        return {
            "product_id": row.product_id,
            "product": row.product,
            "img_url": row.img_url,
        }

    def mark_facebook_posted(self, product_id: int):
        query = """
        UPDATE dbo.Products
        SET facebook_featured_at = GETDATE()
        WHERE product_id = ?
        """
        self.cursor.execute(query, product_id)
        self.conn.commit()
