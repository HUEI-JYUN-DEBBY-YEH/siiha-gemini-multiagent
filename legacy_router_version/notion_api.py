import requests
import datetime
from config import NOTION_API_KEY, NOTION_DATABASE_ID

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_API_VERSION = "2022-06-28"

MAX_NOTION_RICH_TEXT_LENGTH = 1900  # 留餘地避免剛好超過 2000 出錯

def truncate_content(content, max_length=MAX_NOTION_RICH_TEXT_LENGTH):
    if len(content) <= max_length:
        return content, None
    else:
        return (
            content[:max_length] + "\n\n[Content truncated due to Notion limit]",
            content[max_length:]
        )

def write_task_to_notion(title, task_description, category, generated_plan, intent, user_message):
    print("[Notion] Start writing task to Notion...")
    print(f"  - Title: {title}")
    print(f"  - Category: {category}")
    print(f"  - Plan: [🤖 Gemini Answer]\n{generated_plan}")
    print(f"  - Intent: {intent}")
    print(f"  - User Message: {user_message}")

    truncated_plan, _ = truncate_content(generated_plan)

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION
    }

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Task": {
                "rich_text": [{"text": {"content": task_description}}]
            },
            "Category": {
                "select": {"name": category}
            },
            "Generated Plan": {
                "rich_text": [{"text": {"content": f"[🤖 Gemini Answer]\n{truncated_plan}"}}]
            },
            "Intent": {
                "rich_text": [{"text": {"content": intent}}]
            },
            "User Message": {
                "rich_text": [{"text": {"content": user_message}}]
            },
            "Created": {
                "date": {"start": datetime.datetime.utcnow().isoformat()}
            }
        }
    }

    response = requests.post(NOTION_API_URL, headers=headers, json=data)

    print(f"[Notion] Status code: {response.status_code}")
    print(f"[Notion] Response: {response.json()}")

    if response.status_code != 200:
        raise Exception(f"[SIIHA] Notion write failed: {response.status_code} {response.text}")

def log_to_notion(task, intent, plan, category="general"):
    """
    包裝write_task_to_notion，讓主程式呼叫簡潔。
    """
    try:
        write_task_to_notion(
            title=task,
            task_description=task,
            category=category,
            generated_plan=plan,
            intent=intent,
            user_message=task
        )
    except Exception as e:
        print(f"[Notion] Logging error: {e}")