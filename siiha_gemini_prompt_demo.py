# siiha_gemini_prompt_demo.py

import gradio as gr
import google.generativeai as genai
from datetime import datetime, timedelta
from config import GOOGLE_API_KEY
from notion_api import write_task_to_notion as log_to_notion
from calendar_api import list_events, create_event, delete_event_by_title, check_availability
from gmail_api import send_email
from parser_utils import parse_datetime_and_title, parse_email_fields

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

intent_examples = {
    "leave": ["I'd like to take a few days off."],
    "burnout": ["😮‍💨 I'm burned out from work."],
    "resignation": ["📉 I'm thinking of quitting."],
    "onboarding": ["🧱 What should I do for new hire onboarding?"],
    "policy": ["📄 What's our remote work policy?"],
    "conflict": ["⚡ Having issues with a teammate."],
    "feedback": ["🧱 How to give constructive feedback?"],
    "recruitment": ["🗑 Draft a job posting for intern."],
    "calendar": ["🗓️ Create a meeting for next week."],
    "email": ["📧 Send an email to my team.", "✅ Check inbox"]
}

def classify_intent(user_input):
    prompt = (
        f"You are an HR assistant. Classify the input into one of these intents:\n"
        f"{', '.join(intent_examples.keys())}\n"
        f"Input: \"{user_input}\"\n"
        f"Respond with only the intent keyword."
    )
    return model.generate_content(prompt).text.strip().lower()

def respond_by_prompt(intent, user_input):
    examples = intent_examples.get(intent, [])
    sample = "\n".join(f"User: {e}\nAI: ..." for e in examples)
    prompt = (
        "You are a caring and helpful HR assistant.\n"
        "Respond warmly in one paragraph. Include both an emotional encouragement and a practical suggestion.\n"
        f"{sample}\nUser: {user_input}\nAI:"
    )
    return model.generate_content(prompt).text.strip()

def fallback_response(user_input):
    prompt = (
        "You are an emotionally intelligent HR assistant.\n"
        "Give a concise, warm answer. Include 1 emotional support and 1 practical step.\n\n"
        f"User: {user_input}\nAI:"
    )
    return model.generate_content(prompt).text.strip()

def handle_calendar_task(user_input):
    action = user_input.lower()
    if "list" in action:
        return list_events()
    elif "available" in action:
        return check_availability("2024-06-10T10:00:00")
    elif "delete" in action:
        return delete_event_by_title("Team Sync")
    else:
        title, start_time_str = parse_datetime_and_title(user_input)
        if title and start_time_str:
            start_dt = datetime.fromisoformat(start_time_str)
            end_dt = start_dt + timedelta(hours=1)
            end_time_str = end_dt.isoformat()
            event = create_event(title, start_time_str=start_time_str, end_time_str=end_time_str, location="Meeting Room A")
            if isinstance(event, dict):
                summary = event.get("summary", "Your event")
                time = event.get("start", {}).get("dateTime", "unknown time")
                link = event.get("htmlLink", "")
                return f"**{summary}** scheduled on {time}. [View event]({link})"
            else:
                return event
        return fallback_response(user_input)

def handle_email_task(user_input):
    to, subject, body = parse_email_fields(user_input)
    if to and body:
        result = send_email(to=to, subject=subject, body_text=body, task_description=user_input)
        if result:
            return f"📧 Email sent to {to} with subject: {subject if subject else '[Auto-Generated]'}"
        else:
            return "⚠️ Email sending failed. Please check inputs."
    return fallback_response(user_input)

def siiha_agent(user_input):
    intent = classify_intent(user_input)
    print(f"[Intent Detected]: {intent}")
    if intent == "calendar":
        response = handle_calendar_task(user_input)
    elif intent == "email":
        response = handle_email_task(user_input)
    elif intent in intent_examples:
        response = respond_by_prompt(intent, user_input)
    else:
        response = fallback_response(user_input)
    return response, intent

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 SIIHA | Gemini HR Assistant × Calendar + Gmail")
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(label="Your message", placeholder="e.g., Please help me send an email...")

    def respond(chat_history, message):
        if not isinstance(chat_history, list):
            chat_history = []

        msg_text = ""
        if isinstance(message, list):
            for msg in reversed(message):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    msg_text = msg.get("content", "")
                    break
        elif isinstance(message, str):
            msg_text = message

        msg_lower = msg_text.lower()
        intent = (
            "email" if "email" in msg_lower or "send" in msg_lower else
            "calendar" if "calendar" in msg_lower or "meeting" in msg_lower else
            "fallback"
        )

        reply_text = ""
        try:
            if intent == "email":
                reply_text = handle_email_task(msg_text)
            elif intent == "calendar":
                reply_text = handle_calendar_task(msg_text)
            else:
                reply_text = fallback_response(msg_text)
        except Exception as e:
            reply_text = f"Something went wrong: {e}"

        try:
            log_to_notion(
                title=msg_text,
                task_description=msg_text,
                category=intent,
                generated_plan=reply_text,
                intent=intent,
                user_message=msg_text
            )
        except Exception as e:
            print(f"[Notion] Logging failed: {e}")

        chat_history.append({"role": "user", "content": msg_text})
        chat_history.append({"role": "assistant", "content": reply_text})
        return chat_history

    msg.submit(respond, [chatbot, msg], chatbot)

    with gr.Row():
        with gr.Column():
            feedback_label = gr.Label(value="", label="Feedback")

        with gr.Column():
            with gr.Row():
                btn_helpful = gr.Button("👍 That was helpful")
                btn_not_helpful = gr.Button("🔁 Not quite what I needed")

    def feedback_fn(feedback: str):
        return f"Thank you for your feedback: {feedback}. SIIHA is here to listen, learn, and grow with you."

    btn_helpful.click(lambda: feedback_fn("That was helpful"), outputs=[feedback_label])
    btn_not_helpful.click(lambda: feedback_fn("Not quite what I needed"), outputs=[feedback_label])

demo.launch()
