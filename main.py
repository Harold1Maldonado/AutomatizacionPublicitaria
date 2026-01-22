from dotenv import load_dotenv
import os
import requests
import sys

from db import DandyDealsDB

load_dotenv()

FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v24.0")
FB_PAGE_ID = (os.getenv("FB_PAGE_ID") or "").strip()
FB_PAGE_ACCESS_TOKEN = (os.getenv("FB_PAGE_ACCESS_TOKEN") or "").strip()

for var_name, var_value in [
    ("FB_PAGE_ID", FB_PAGE_ID),
    ("FB_PAGE_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN),
]:
    if not var_value:
        raise RuntimeError(f"Falta variable de entorno: {var_name}")

DRY_RUN = "--dry-run" in sys.argv


def parse_max_posts(argv: list[str]) -> int:
    """
    Lee --max-posts N de la línea de comandos.
    Default = 1
    """
    if "--max-posts" not in argv:
        return 1
    idx = argv.index("--max-posts")
    if idx == len(argv) - 1:
        raise RuntimeError("Uso: python main.py [--dry-run] [--max-posts N]")
    try:
        n = int(argv[idx + 1])
    except ValueError:
        raise RuntimeError("El valor de --max-posts debe ser un entero.")
    if n < 1 or n > 20:
        raise RuntimeError("--max-posts debe estar entre 1 y 20 (seguridad).")
    return n


MAX_POSTS = parse_max_posts(sys.argv)


def post_photo(image_url: str, message: str) -> dict:
    endpoint = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{FB_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "message": message,
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "published": "true",
    }

    r = requests.post(endpoint, data=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Facebook error ({r.status_code}): {r.text}")
    return r.json()


def build_message(product_name: str) -> str:
    return f"Nuevo artículo destacado: {product_name}"


if __name__ == "__main__":
    print("DRY_RUN:", DRY_RUN)
    print("MAX_POSTS:", MAX_POSTS)

    db = DandyDealsDB()
    try:
        posted = 0

        while posted < MAX_POSTS:
            item = db.get_next_featured_for_facebook()
            if not item:
                if posted == 0:
                    print("There are not Feature Products for Facebook.")
                else:
                    print("No more pending Feature Products.")
                break

            product_id = item["product_id"]
            product_name = item["product"]
            img_url = item["img_url"]
            message = build_message(product_name)

            print(f"\nSeleccionado product_id={product_id}")
            print(f"Imagen: {img_url}")
            print(f"Mensaje: {message}")

            if DRY_RUN:
                print("DRY RUN activo - No publishing - No DB update.")
                posted += 1
                break

            resp = post_photo(image_url=img_url, message=message)
            print("Facebook OK:", resp)

            db.mark_facebook_posted(product_id)
            print("DB OK: marcado facebook_featured_at.")

            posted += 1

        print(f"\nCompleted. Processed posts: {posted}")

    finally:
        db.close()
