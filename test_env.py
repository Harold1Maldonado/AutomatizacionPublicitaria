from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=env_path, override=True)

print("ENV PATH:", env_path)
print("FB_PAGE_ID:", os.getenv("FB_PAGE_ID"))
print("FB_GRAPH_VERSION:", os.getenv("FB_GRAPH_VERSION"))
print("TOKEN START:", (os.getenv("FB_PAGE_ACCESS_TOKEN") or "")[:10])
