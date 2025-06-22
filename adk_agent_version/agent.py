
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from siiha_adk.gmail_api import send_email, list_emails, delete_email_by_subject
from siiha_adk.calendar_api import create_event, list_events, delete_event_by_title
from siiha_adk.notion_api import log_to_notion

load_dotenv(dotenv_path=".env")
logger = logging.getLogger(__name__)

# 📬 Gmail 工具 with Notion 日誌
async def gmail_tool(action: str, parameters: dict) -> str:
    result = ""
    try:
        if action in ["send_email", "email", "notify"]:
            result = await asyncio.to_thread(send_email, to=parameters.get("to") or parameters.get("recipient"),
                                             subject=parameters.get("subject"),
                                             body_text=parameters.get("body"))
        elif action in ["list_emails", "read_emails"]:
            result = await asyncio.to_thread(list_emails, max_results=parameters.get("max_results", 5))
        elif action in ["delete_email_by_subject", "delete_email"]:
            result = await asyncio.to_thread(delete_email_by_subject, subject_keyword=parameters.get("subject_keyword"))
        else:
            result = f"Unknown Gmail action: {action}"
    except Exception as e:
        result = f"GmailTool Error: {str(e)}"

    try:
        content = f"[GmailTool] Action: {action}, Parameters: {parameters}, Result: {result}"
        await asyncio.to_thread(log_to_notion, task=content, intent="gmail-action", plan="Auto-log from SIIHA tool.", category="gmail")
    except Exception as log_e:
        result += f" | NotionLog Error: {str(log_e)}"
    return result

# 📅 Calendar 工具 with Notion 日誌
async def calendar_tool(action: str, parameters: dict) -> str:
    result = ""
    try:
        if action in ["create_event", "schedule_meeting", "create_meeting", "add_calendar"]:
            result = await asyncio.to_thread(create_event,
                                             title=parameters.get("title", "Meeting with " + ", ".join(parameters.get("attendees", []))),
                                             start_time_str=parameters.get("start_time") or f"{parameters.get('date')}T{parameters.get('time')}",
                                             end_time_str=parameters.get("end_time"),
                                             location=parameters.get("location", ""))
        elif action in ["list_events", "show_events"]:
            result = await asyncio.to_thread(list_events, max_results=parameters.get("max_results", 10))
        elif action in ["delete_event_by_title", "delete_event"]:
            result = await asyncio.to_thread(delete_event_by_title, title=parameters.get("title"))
        else:
            result = f"Unknown Calendar action: {action}"
    except Exception as e:
        result = f"CalendarTool Error: {str(e)}"

    try:
        content = f"[CalendarTool] Action: {action}, Parameters: {parameters}, Result: {result}"
        await asyncio.to_thread(log_to_notion, task=content, intent="calendar-action", plan="Auto-log from SIIHA tool.", category="calendar")
    except Exception as log_e:
        result += f" | NotionLog Error: {str(log_e)}"
    return result

# 🗒️ Notion 工具 with self-log
async def notion_tool(content: str) -> str:
    result = ""
    try:
        await asyncio.to_thread(log_to_notion, task=content, intent="notion-log", plan="User log request", category="notion")
        result = f"Logged to Notion: '{content[:50]}...'"
    except Exception as e:
        result = f"NotionTool Error: {str(e)}"

    try:
        summary = f"[NotionTool] Log content: {content}, Result: {result}"
        await asyncio.to_thread(log_to_notion, task=summary, intent="notion-log-meta", plan="Auto-log from SIIHA tool.", category="notion")
    except Exception as log_e:
        result += f" | NotionLog Error: {str(log_e)}"
    return result

# 🧠 LLM Agent with All Tools
root_agent = LlmAgent(
    name="siiha_functiontool_agent",
    model="gemini-2.0-flash-001",
    instruction=(
        "You are SIIHA, a smart assistant for Gmail, Calendar, and Notion. "
        "Use the tools to complete user tasks. Respond kindly if tools are not applicable. "
        f"Today is {datetime.now().strftime('%Y-%m-%d')}."
    ),
    tools=[
        FunctionTool(gmail_tool),
        FunctionTool(calendar_tool),
        FunctionTool(notion_tool),
    ]
)
