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


if __name__ == "__main__":
    mcp.run()