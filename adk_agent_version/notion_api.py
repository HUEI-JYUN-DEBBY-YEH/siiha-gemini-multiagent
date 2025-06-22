# notion_api.py
import requests
import datetime
import os

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_API_VERSION = "2022-06-28"

def log_to_notion(task: str, intent: str, plan: str, category: str):
    notion_api_key = os.getenv("NOTION_TOKEN")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    if not notion_api_key or not notion_database_id:
        print("[Notion] Error: NOTION_TOKEN or NOTION_DATABASE_ID not set in .env file.")
        return

    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION
    }

    truncated_task = task[:1999]

    data = {
        "parent": {"database_id": notion_database_id},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"({category.upper()}) {truncated_task}"}}]
            },
            "Task": {
                "rich_text": [{"text": {"content": task}}]
            },
            "Category": {
                "select": {"name": category}
            },
            "Generated Plan": {
                "rich_text": [{"text": {"content": plan}}]
            },
            "Intent": {
                "rich_text": [{"text": {"content": intent}}]
            },
            "Created": {
                "date": {"start": datetime.datetime.utcnow().isoformat()}
            }
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, json=data)
        response.raise_for_status()
        print(f"[Notion] Logged task successfully to Notion.")
    except requests.exceptions.RequestException as e:
        print(f"[Notion] Logging error: {e}")
        print(f"[Notion] Response body: {e.response.text if e.response else 'No response'}")
