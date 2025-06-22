
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/calendar"])
    service = build("calendar", "v3", credentials=creds)
    return service


def list_events(max_results=10):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])
    return events


def create_event(title, start_time_str, end_time_str, location=None, timezone="Asia/Taipei"):
    service = get_calendar_service()

    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

    tz = pytz.timezone(timezone)
    start_time = tz.localize(start_time).isoformat()
    end_time = tz.localize(end_time).isoformat()

    event = {
        "summary": title,
        "location": location,
        "start": {"dateTime": start_time, "timeZone": timezone},
        "end": {"dateTime": end_time, "timeZone": timezone},
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event


def delete_event_by_title(title):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=50, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])
    for event in events:
        if event["summary"] == title:
            service.events().delete(calendarId="primary", eventId=event["id"]).execute()
            return f"Deleted event: {title}"
    return "Event not found."


def check_availability(start_time_str, end_time_str, timezone="Asia/Taipei"):
    service = get_calendar_service()

    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

    tz = pytz.timezone(timezone)
    start_time = tz.localize(start_time).isoformat()
    end_time = tz.localize(end_time).isoformat()

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "timeZone": timezone,
        "items": [{"id": "primary"}],
    }

    freebusy_result = service.freebusy().query(body=body).execute()
    busy_times = freebusy_result["calendars"]["primary"]["busy"]
    return not busy_times  # True if free, False if busy
