import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion = Client(auth=os.environ["NOTION_TOKEN"])
db = notion.data_sources.retrieve(data_source_id=os.environ["NOTION_DATA_SOURCE_ID"])

for name, prop in db["properties"].items():
    print(f"{name!r}: {prop['type']}")