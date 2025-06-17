
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
from google.oauth2.credentials import Credentials
from config import GMAIL_SCOPES

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(recipient, subject, body_text):
    service = get_gmail_service()
    message = MIMEText(body_text)
    message['to'] = recipient
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    sent_message = service.users().messages().send(userId='me', body=message).execute()
    return sent_message

def list_recent_emails(max_results=5):
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    email_data = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet')
        email_data.append(snippet)
    return email_data

def delete_email_by_subject(subject):
    service = get_gmail_service()
    response = service.users().messages().list(userId='me', q=f'subject:{subject}').execute()
    messages = response.get('messages', [])
    deleted_ids = []
    for msg in messages:
        service.users().messages().delete(userId='me', id=msg['id']).execute()
        deleted_ids.append(msg['id'])
    return deleted_ids
