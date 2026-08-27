import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATA_SOURCE_ID = os.environ["NOTION_DATA_SOURCE_ID"]
DIRECTORY_DS_ID = os.environ["NOTION_DIRECTORY_DATA_SOURCE_ID"]

# --- Phase 1: the ten straightforward columns ---
phase1 = {
    "Status": {"select": {"options": [
        {"name": "Researching"}, {"name": "To Apply"}, {"name": "Applied"},
        {"name": "Interviewing"}, {"name": "Offer"}, {"name": "Closed"},
    ]}},
    "Tier": {"select": {"options": [
        {"name": "Tier 1"}, {"name": "Tier 2"},
        {"name": "Watchlist"}, {"name": "Landscape"},
    ]}},
    "Notes": {"rich_text": {}},
    "News": {"rich_text": {}},
    "Products": {"multi_select": {"options": [
        {"name": "Food waste"}, {"name": "Climate"},
        {"name": "Civic tech"}, {"name": "Sustainability"},
    ]}},
    "Company Size": {"select": {"options": [
        {"name": "1-10"}, {"name": "11-50"}, {"name": "51-200"},
        {"name": "201-1000"}, {"name": "1000+"},
    ]}},
    "Funding / Valuation": {"rich_text": {}},
    "Growth Stage": {"select": {"options": [
        {"name": "Seed"}, {"name": "Early"}, {"name": "Growth"},
        {"name": "Mature"}, {"name": "Declining"},
    ]}},
    "Employees of Interest": {"rich_text": {}},
    "Traction": {"rich_text": {}},
}

print("Phase 1: adding ten columns...")
notion.data_sources.update(data_source_id=DATA_SOURCE_ID, properties=phase1)
print("Phase 1 done.\n")

# --- Phase 2: Competitors self-relation (Companies -> Companies) ---
print("Phase 2: adding Competitors self-relation...")
try:
    notion.data_sources.update(
        data_source_id=DATA_SOURCE_ID,
        properties={"Competitors": {"relation": {
            "data_source_id": DATA_SOURCE_ID,
            "type": "dual_property",
            "dual_property": {},
        }}},
    )
    print("Phase 2 done.\n")
except Exception as e:
    print(f"Phase 2 FAILED (Phase 1 is still fine): {e}\n")

# --- Phase 3: People cross-relation (Companies -> Directory) ---
print("Phase 3: adding People relation to Directory...")
try:
    notion.data_sources.update(
        data_source_id=DATA_SOURCE_ID,
        properties={"People": {"relation": {
            "data_source_id": DIRECTORY_DS_ID,
            "type": "dual_property",
            "dual_property": {},
        }}},
    )
    print("Phase 3 done.\n")
except Exception as e:
    print(f"Phase 3 FAILED (earlier phases still fine): {e}\n")

print("Setup complete. Run inspect_schema.py to verify.")