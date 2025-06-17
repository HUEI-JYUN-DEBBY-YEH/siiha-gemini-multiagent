
from prompt_templates import prompt_response_templates
from calendar_agent_integration import handle_calendar_intent
from gmail_api import send_email, read_email, delete_email
from parser_utils import parse_email_fields

def handle_gmail_intent(intent, user_input, context):
    if intent == "send_email":
        return send_email(user_input)
    elif intent == "read_email":
        return read_email()
    elif intent == "delete_email":
        return delete_email(user_input)
    else:
        return "Sorry, I couldn't process your email request."

def handle_email_task(user_input):
    to, subject, body = parse_email_fields(user_input)
    if to:
        return send_email(to, subject, body)
    else:
        return "Sorry, I could't find a valid email address in your message"
    
def generate_prompt_response(intent, user_input, context):
    template = prompt_response_templates.get(intent, "I'm here to help with that.")
    return template.format(user_input=user_input)

def route_intent(intent, user_input, context):
    # 🔁 Normalize broad intents
    if intent == "calendar":
        intent = "calendar_create"

    if intent in ["calendar_create", "calendar_list", "calendar_delete", "calendar_check"]:
        return handle_calendar_intent(intent, user_input, context)

    elif intent in ["send_email", "read_email", "delete_email"]:
        return handle_gmail_intent(intent, user_input, context)

    else:
        return generate_prompt_response(intent, user_input, context)
