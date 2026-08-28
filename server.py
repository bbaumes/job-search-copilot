import os
from dotenv import load_dotenv
from notion_client import Client
from mcp.server.fastmcp import FastMCP

load_dotenv()

notion = Client(auth=os.environ["NOTION_TOKEN"])
DATA_SOURCE_ID = os.environ["NOTION_DATA_SOURCE_ID"]

mcp = FastMCP("job-search-copilot")


@mcp.tool()
def list_target_companies() -> str:
    """List all target companies from the job search Notion database."""
    response = notion.data_sources.query(data_source_id=DATA_SOURCE_ID)

    lines = []
    for page in response["results"]:
        name = _read_title(page["properties"])
        lines.append(name)

    if not lines:
        return "No companies found."

    return "\n".join(lines)


def _read_title(props: dict) -> str:
    """Pull the title text out of whichever property is the title column."""
    for value in props.values():
        if value["type"] == "title":
            items = value["title"]
            return items[0]["plain_text"] if items else "(untitled)"
    return "(no title)"
# Valid options for the select fields — must match Notion exactly.
VALID_TIERS = {"Tier 1", "Tier 2", "Watchlist", "Landscape"}
VALID_STATUSES = {"Researching", "To Apply", "Applied", "Interviewing", "Offer", "Closed"}
ERROR_VALUE = "ERROR: select valid value"


@mcp.tool()
def add_company(name: str, tier: str, status: str) -> str:
    """Add a new company to the job search database. Tier must be one of:
    Tier 1, Tier 2, Watchlist, Landscape. Status must be one of: Researching,
    To Apply, Applied, Interviewing, Offer, Closed."""

    # Lenient-but-loud validation: use the value if it's valid exactly,
    # otherwise fall back to the visible error sentinel.
    tier_value = tier if tier in VALID_TIERS else ERROR_VALUE
    status_value = status if status in VALID_STATUSES else ERROR_VALUE

    # Create the row. Each property type needs its own JSON shape:
    notion.pages.create(
        parent={"type": "data_source_id", "data_source_id": DATA_SOURCE_ID},
        properties={
            "Company": {"title": [{"text": {"content": name}}]},  # title shape
            "Tier": {"select": {"name": tier_value}},              # select shape
            "Status": {"select": {"name": status_value}},          # select shape
        },
    )

    # Report back — and flag if anything fell back to the error value.
    problems = []
    if tier_value == ERROR_VALUE:
        problems.append(f"tier '{tier}' was invalid")
    if status_value == ERROR_VALUE:
        problems.append(f"status '{status}' was invalid")

    if problems:
        return f"Added '{name}', but {' and '.join(problems)} — flagged in the table for you to fix."
    return f"Added '{name}' (Tier: {tier_value}, Status: {status_value})."
    
# ============================================================
# TOOL 3: update_status — modify an existing company's status
# ============================================================
@mcp.tool()
def update_status(company_name: str, new_status: str) -> str:
    """Update the Status of an existing company in the job search database.
    Finds the company by name (partial, case-insensitive match). Status must be
    one of: Researching, To Apply, Applied, Interviewing, Offer, Closed."""

    # Guard 1: refuse an invalid status rather than corrupting a good row.
    if new_status not in VALID_STATUSES:
        valid = ", ".join(sorted(VALID_STATUSES))
        return f"'{new_status}' isn't a valid status. Must be one of: {valid}. Nothing changed."

    # Find matching companies (partial, case-insensitive).
    response = notion.data_sources.query(data_source_id=DATA_SOURCE_ID)
    query = company_name.lower()
    matches = []
    for page in response["results"]:
        name = _read_title(page["properties"])
        if query in name.lower():
            matches.append((name, page["id"]))

    # Guard 2: act only on a unique match.
    if len(matches) == 0:
        return f"No company matching '{company_name}' found. Nothing changed."
    if len(matches) > 1:
        names = ", ".join(f"'{n}'" for n, _ in matches)
        return (f"'{company_name}' matched {len(matches)} companies: {names}. "
                f"Be more specific — nothing changed.")

    # Exactly one match — safe to update.
    matched_name, page_id = matches[0]
    notion.pages.update(
        page_id=page_id,
        properties={"Status": {"select": {"name": new_status}}},
    )
    return f"Updated '{matched_name}' status to {new_status}."

if __name__ == "__main__":
    mcp.run()