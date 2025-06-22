# calendar_api.py
import os
import json
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 使用環境變數，並提供預設路徑
credentials_path = os.getenv("OAUTH_CREDENTIALS_PATH", "./credentials/credentials.json")
token_path = os.getenv("OAUTH_TOKEN_PATH", "./credentials/token.json")

def get_calendar_service():
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    return build("calendar", "v3", credentials=creds)

def create_event(title: str, start_time_str: str, end_time_str: str = None, location: str = ""):
    service = get_calendar_service()
    try:
        now = datetime.utcnow()
        if "today" in start_time_str.lower():
            hour_part = start_time_str.lower().replace("today", "").strip()
            start_hour = int(hour_part.replace("pm", "").replace("am", ""))
            if "pm" in hour_part.lower():
                start_hour += 12
            start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        else:
            start_time = datetime.fromisoformat(start_time_str)

        end_time = start_time + timedelta(hours=1) if not end_time_str else datetime.fromisoformat(end_time_str)

        event = {
            "summary": title,
            "location": location,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Taipei"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Taipei"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return json.dumps({
            "status": "success",
            "result": f"Event created: {created_event.get('htmlLink')}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"An error occurred while creating event: {e}"
        }, ensure_ascii=False)

def list_events(max_results=10):
    service = get_calendar_service()
    try:
        now = datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary", timeMin=now, maxResults=max_results,
            singleEvents=True, orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return json.dumps({"status": "success", "result": "No upcoming events found."}, ensure_ascii=False)

        summaries = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            summaries.append(f"{start} - {summary}")

        return json.dumps({"status": "success", "result": "\n".join(summaries)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error listing events: {e}"}, ensure_ascii=False)

def delete_event_by_title(title: str):
    service = get_calendar_service()
    try:
        now = datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary", q=title, timeMin=now,
            maxResults=50, singleEvents=True
        ).execute()
        events = events_result.get("items", [])
        deleted = 0

        for event in events:
            if event.get("summary") == title:
                service.events().delete(calendarId="primary", eventId=event["id"]).execute()
                deleted += 1

        if deleted:
            return json.dumps({"status": "success", "result": f"Deleted {deleted} event(s) titled '{title}'."}, ensure_ascii=False)
        else:
            return json.dumps({"status": "success", "result": f"No exact match found for '{title}'."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error deleting event: {e}"}, ensure_ascii=False)
