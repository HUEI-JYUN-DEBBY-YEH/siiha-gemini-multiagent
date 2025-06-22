from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def list_events(max_results=10):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])
    return events

def create_event(title, start_time, end_time, location=""):
    service = get_calendar_service()
    event = {
        "summary": title,
        "location": location,
        "start": {"dateTime": start_time, "timeZone": "Asia/Taipei"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Taipei"},
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event.get("htmlLink")

def delete_event_by_title(title):
    service = get_calendar_service()
    events = list_events(50)
    deleted = []
    for event in events:
        if event["summary"].lower() == title.lower():
            service.events().delete(calendarId="primary", eventId=event["id"]).execute()
            deleted.append(event["summary"])
    return deleted

def check_availability(target_time, duration_minutes=30):
    service = get_calendar_service()
    start_time = datetime.datetime.fromisoformat(target_time)
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    busy = service.freebusy().query(
        body={
            "timeMin": start_time.isoformat() + "Z",
            "timeMax": end_time.isoformat() + "Z",
            "timeZone": "Asia/Taipei",
            "items": [{"id": "primary"}],
        }
    ).execute()
    return not busy["calendars"]["primary"].get("busy")
