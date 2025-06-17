# parser_utils.py

from datetime import datetime, timedelta
import re

def get_next_weekday(target_weekday: int):
    """
    傳回下一個指定 weekday 的 datetime（若今天就是該 weekday，回傳 today）
    """
    today = datetime.now()
    days_ahead = (target_weekday - today.weekday()) % 7
    return today + timedelta(days=days_ahead)

def parse_datetime_and_title(text):
    """
    擷取使用者輸入中的日期與主題資訊，回傳(title, iso_time)
    """
    # 偵測時間格式（e.g., 2pm, 14:00, 10am）
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
    hour, minute, meridiem = None, 0, None

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)

        if meridiem:
            if meridiem.lower() == "pm" and hour < 12:
                hour += 12
            elif meridiem.lower() == "am" and hour == 12:
                hour = 0

    # 偵測日期文字
    today = datetime.now()
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, 
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    event_date = today
    lowered = text.lower()

    for day_text, weekday_num in weekdays.items():
        if day_text in lowered:
            event_date = get_next_weekday(weekday_num)
            break

    if "tomorrow" in lowered:
        event_date = today + timedelta(days=1)

    # 組合 ISO 時間格式
    if hour is not None:
        event_datetime = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        iso_time = event_datetime.isoformat()
    else:
        iso_time = None

    # 嘗試從句中找主題
    title_match = re.search(
        r"(meeting with [\w\s]+|team sync|catch up|standup|discussion|1:1|review|check[- ]in|team meeting)", 
        lowered
    )
    title = title_match.group(0).title() if title_match else "Team Meeting"

    return title, iso_time

def parse_email_fields(text):
    """
    擷取 email 中的 to, subject, body
    e.g., Please email to X with subject \"Y\" and body \"Z\"
    """
    to_match = re.search(r"to\s+(\S+@\S+)", text)
    subject_match = re.search(r'subject\s+"(.*)"', text)
    body_match = re.search(r'body\s+"(.*?)"', text)

    to = to_match.group(1) if to_match else None
    subject = subject_match.group(1) if subject_match else "No Subject"
    body = body_match.group(1) if body_match else "No Content"
    return to, subject, body
