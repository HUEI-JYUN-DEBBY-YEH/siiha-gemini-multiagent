# gmail_api.py
import os
import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

credentials_path = os.getenv("OAUTH_CREDENTIALS_PATH", "./credentials/credentials.json")
token_path = os.getenv("OAUTH_TOKEN_PATH", "./credentials/token.json")

def get_gmail_service():
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    return build("gmail", "v1", credentials=creds)

def send_email(to: str, subject: str, body_text: str):
    service = get_gmail_service()
    message = MIMEText(body_text)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    try:
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return json.dumps({
            "status": "success",
            "result": f"Email sent. ID: {sent['id']}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to send email: {e}"
        }, ensure_ascii=False)

def list_emails(max_results=5):
    service = get_gmail_service()
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        if not messages:
            return json.dumps({"status": "success", "result": "No emails found."}, ensure_ascii=False)

        emails = []
        for msg in messages:
            detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = detail.get('payload', {}).get('headers', [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            emails.append(f"From: {sender}, Subject: {subject}")

        return json.dumps({"status": "success", "result": "\n".join(emails)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to fetch emails: {e}"}, ensure_ascii=False)

def delete_email_by_subject(subject_keyword: str):
    service = get_gmail_service()
    try:
        results = service.users().messages().list(userId='me', q=f"subject:{subject_keyword}").execute()
        messages = results.get("messages", [])
        if not messages:
            return json.dumps({
                "status": "success",
                "result": f"No emails found with subject '{subject_keyword}'."
            }, ensure_ascii=False)

        for msg in messages:
            service.users().messages().delete(userId='me', id=msg['id']).execute()

        return json.dumps({
            "status": "success",
            "result": f"Deleted {len(messages)} email(s) with subject '{subject_keyword}'."
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error deleting emails: {e}"}, ensure_ascii=False)
