from notion_client import Client
import os

NOTION_API_KEY = "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"
notion = Client(auth=NOTION_API_KEY)

def create_hr_task_database():
    print("[SIIHA] Creating HR Tasks database...")

    # ✅ 指定正確的 parent page ID
    parent_page_id = "2095118474d2801f9d98c3a382ea110c"

    response = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "HR Tasks"}}],
        properties={
            "Name": {"title": {}},
            "Task": {"rich_text": {}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "Recruitment", "color": "blue"},
                        {"name": "Onboarding", "color": "green"},
                        {"name": "Performance", "color": "red"},
                        {"name": "Emotion", "color": "purple"},
                    ]
                }
            },
            "Intent": {"rich_text": {}},
            "User Message": {"rich_text": {}},
            "Generated Plan": {"rich_text": {}},
            "Created": {"date": {}},
        },
    )

    print(f"[SIIHA] Database created successfully! ✅ Database ID: {response['id']}")
    return response['id']

if __name__ == "__main__":
    create_hr_task_database()
