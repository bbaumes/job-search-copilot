import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion = Client(auth=os.environ["NOTION_TOKEN"])

DIRECTORY_DB_ID = "cde5cef201b382caa2e8017112cd68da"

db = notion.databases.retrieve(database_id=DIRECTORY_DB_ID)
for ds in db["data_sources"]:
    print(f"Data source: {ds['id']}  (name: {ds['name']})")