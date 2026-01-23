# main.py
from __future__ import annotations

from dotenv import load_dotenv
import os
import sys
import json
import time
import requests

from db import DandyDealsDB

load_dotenv()

FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v24.0").strip()
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
    Default = 3
    Seguridad: 1..3 (porque un post será de hasta 3 fotos).
    """
    if "--max-posts" not in argv:
        return 3

    idx = argv.index("--max-posts")
    if idx == len(argv) - 1:
        raise RuntimeError("Uso: python main.py [--dry-run] [--max-posts N]")

    try:
        n = int(argv[idx + 1])
    except ValueError:
        raise RuntimeError("El valor de --max-posts debe ser un entero.")

    if n < 1 or n > 3:
        raise RuntimeError("--max-posts debe estar entre 1 y 3.")
    return n


MAX_POSTS = parse_max_posts(sys.argv)


def post_form_with_retries(
    endpoint: str,
    payload: dict,
    *,
    timeout: int = 30,
    tries: int = 3,
    backoff_seconds: float = 1.0,
) -> dict:
    """
    POST x-www-form-urlencoded a Graph API con reintentos cortos (útil para 500 intermitentes).
    Valida también casos de 200 con {"error": ...}.
    """
    last_status = None
    last_data = None

    for attempt in range(1, tries + 1):
        r = requests.post(endpoint, data=payload, timeout=timeout)

        # Intenta parsear JSON; si no, conserva el raw
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}

        ok = (r.status_code < 400) and ("error" not in data)
        if ok:
            return data

        last_status = r.status_code
        last_data = data

        # Reintentar sólo en 500 (o errores genéricos)
        if r.status_code == 500 and attempt < tries:
            # backoff exponencial suave
            sleep_for = backoff_seconds * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        break

    raise RuntimeError(
        f"Facebook error ({last_status}) en endpoint: {endpoint} | resp: {last_data}")


def upload_photo_unpublished(image_url: str) -> str:
    """
    Sube una foto a Facebook como no publicada y devuelve su media_fbid.
    """
    endpoint = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{FB_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "access_token": FB_PAGE_ACCESS_TOKEN,
        # Para Graph, esto suele funcionar bien como string.
        # Si quieres probar boolean, cámbialo a False.
        "published": "false",
    }

    data = post_form_with_retries(endpoint, payload, tries=3)

    if "id" not in data:
        raise RuntimeError(
            f"Respuesta inesperada de Facebook en /photos: {data}")

    return data["id"]


def create_feed_post_with_media(message: str, media_fbids: list[str]) -> dict:
    """
    Crea un post en el feed con varias fotos adjuntas.

    IMPORTANTE: attached_media[*] debe ir como string JSON, no como dict Python.
    """
    endpoint = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{FB_PAGE_ID}/feed"
    payload: dict = {
        "message": message,
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }

    # attached_media[0]={"media_fbid":"..."} como JSON string
    for idx, fbid in enumerate(media_fbids):
        payload[f"attached_media[{idx}]"] = json.dumps({"media_fbid": fbid})

    return post_form_with_retries(endpoint, payload, tries=3)


def build_multi_message(items: list[dict]) -> str:
    header = (
        "Lots of new games in the shop and going on ebay soon!\n"
        "Feel free to comment or send a DM to claim your copy today.\n"
    )

    lines: list[str] = []
    for it in items:
        # Nota: incluir img_url en el texto no es obligatorio (las fotos ya van adjuntas),
        # pero lo mantengo para no cambiar tu formato.
        lines.append(f'{it["product"]} - {it["list_price"]} - {it["img_url"]}')

    return header + "\n\n" + "\n".join(lines)


if __name__ == "__main__":
    print("DRY_RUN:", DRY_RUN)
    print("MAX_POSTS:", MAX_POSTS)
    print("FB_GRAPH_VERSION:", FB_GRAPH_VERSION)

    db = DandyDealsDB()
    try:
        items = db.get_featured_batch_for_facebook(limit=MAX_POSTS)

        if not items:
            print("No hay productos destacados pendientes para Facebook.")
            raise SystemExit(0)

        message = build_multi_message(items)

        print("\nProductos seleccionados:")
        for it in items:
            print(
                f'- product_id={it["product_id"]} | {it["product"]} | {it["list_price"]}')
            print(f'  img: {it["img_url"]}')

        print("\nMensaje a publicar:\n")
        print(message)

        if DRY_RUN:
            print("\nDRY RUN activo: no se publica y no se actualiza la DB.")
            raise SystemExit(0)

        # Subir fotos como no publicadas
        media_fbids: list[str] = []
        for it in items:
            fbid = upload_photo_unpublished(it["img_url"])
            media_fbids.append(fbid)

        #  Crear post con fotos adjuntas
        resp = create_feed_post_with_media(
            message=message, media_fbids=media_fbids)
        print("\nFacebook OK:", resp)

        #  Marcar en DB como publicado
        db.mark_facebook_posted_many([it["product_id"] for it in items])
        print("DB OK: marcado facebook_featured_at para los productos publicados.")

        print(f"\nCompleted. Publicados en este lote: {len(items)}")

    finally:
        db.close()

# pipenv run python main.py
# pipenv run python main.py --dry-run
# pipenv run python main.py --max-posts 3
