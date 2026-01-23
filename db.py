import pyodbc
from config import DB_CONNECTION


class DandyDealsDB:
    def __init__(self):
        self.conn = pyodbc.connect(DB_CONNECTION)
        self.cursor = self.conn.cursor()

    def close(self):
        try:
            self.cursor.close()
        finally:
            self.conn.close()

    def get_featured_batch_for_facebook(self, limit: int = 3) -> list[dict]:
        """
        Devuelve hasta `limit` productos con:
          featured = 1
          facebook_featured_at IS NULL
          y con al menos una imagen (elige la primera por secuencia).
          date_added_to_sheet ASC (más antiguos primero).
        """
        if limit < 1:
            return []

        query = f"""
        SELECT TOP ({limit})
            p.product_id,
            p.product,
            p.list_price,
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
        rows = self.cursor.fetchall()

        items: list[dict] = []
        for r in rows:
            items.append(
                {
                    "product_id": int(r.product_id),
                    "product": r.product,
                    "list_price": r.list_price,
                    "img_url": r.img_url,
                }
            )

        return items

    def mark_facebook_posted_many(self, product_ids: list[int]) -> None:
        """
        Set facebook_featured_at = GETDATE() para una lista de product_id.
        """
        if not product_ids:
            return

        placeholders = ",".join("?" for _ in product_ids)
        query = f"""
        UPDATE dbo.Products
        SET facebook_featured_at = GETDATE()
        WHERE product_id IN ({placeholders})
        """

        self.cursor.execute(query, *product_ids)
        self.conn.commit()
