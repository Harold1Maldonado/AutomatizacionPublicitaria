from dotenv import load_dotenv
import os
import requests

from pathlib import Path
env_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=env_path, override=True)
print("ENV PATH:", env_path)

for var in ["FB_PAGE_ID", "FB_PAGE_ACCESS_TOKEN", "FB_GRAPH_VERSION"]:
    if not os.getenv(var):
        raise RuntimeError(f"Falta variable de entorno: {var}")

print("ENV cargado correctamente")

FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v24.0")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

print("Token length:", len(FB_PAGE_ACCESS_TOKEN or ""))
print("Token startswith:", (FB_PAGE_ACCESS_TOKEN or "")[:10])
print("Has spaces:", " " in (FB_PAGE_ACCESS_TOKEN or ""))


def post_photo(image_url: str, caption: str) -> dict:
    endpoint = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{FB_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "published": "true",
    }

    r = requests.post(endpoint, data=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Facebook error ({r.status_code}): {r.text}")

    return r.json()


if __name__ == "__main__":
    resp = post_photo(
        image_url="https://images.pexels.com/photos/33903442/pexels-photo-33903442.jpeg",
        caption="Prueba desde script Python con Graph API a las 18:45",
    )
    print(resp)
