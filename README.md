# SIIHA: Gemini Multi-Agent System for Human-Centered Productivity

> **System for Intelligent Interaction with Human Agency**

SIIHA is a lightweight AI assistant prototype built with Google Gemini, designed to coordinate with Gmail, Google Calendar, and Notion using function calling. This system interprets user intent in natural language and dispatches tasks to appropriate tools, forming a personalized multi-agent workspace.

---

## 🔧 Features

- ✉️ **Gmail Agent**: Send emails using natural language instructions
- 📅 **Calendar Agent**: Create events with semantic time/date expressions
- 🗒️ **Notion Agent**: Log agent actions or user messages into a Notion database
- 🤖 **Gemini Function Calling**: Automatically routes tasks based on user intent
- 📡 **Async JSON-based function core**: Modular dispatch layer for new integrations

---

## 🌐 Tech Stack

- **Gemini Pro API** (function_calling enabled)
- **Google OAuth2 APIs**: Gmail / Calendar / Notion SDK
- **FastAPI** (for local UI interaction)
- **Python 3.10** + `google-api-python-client`, `notion-client`, `jinja2`

---

## 🖥️ Folder Structure

```bash
📂 siiha-gemini-multiagent/
├── siiha_gemini_prompt_demo.py       # Entry point with Gradio Interface
├── function_router.py                # Intent routing logic

# ➤ Gmail Agent
├── gmail_api.py                      # Gmail sender
├── gmail_utils.py                    # Gmail parser utils

# ➤ Calendar Agent
├── calendar_api.py                   # Google Calendar integration
├── calendar_utils.py                 # Time parser functions

# ➤ Notion Agent
├── notion_api.py                     # Notion database integration

# ➤ Config & Core
├── config.py                         # Constants & config
├── parser_utils.py                   # General time parser

# ➤ Setup
├── create_notion_db.py               # Notion DB creation
├── quickstart.py                     # OAuth helper script
├── requirements.txt                  # Python dependencies
├── .env / env/                       # Local secrets folder
├── token.json                        # OAuth token file
├── credentials.json                  # (Optional) GCP API Key

# ➤ Demo & Docs
├── *.mp4                             # Demo videos
├── README.md                         # Project intro & usage guide

```

---

## 🚀 How to Run (Local)

1. **Prepare Secrets**: Place your OAuth tokens 

```bash
├── token.json
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run FastAPI Server**

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

4. **Try Instructions**

```text
Please send an email to debby83317@gmail.com with subject "Testing" and body "SIIHA working!"
Add a meeting titled "Team Sync" tomorrow at 3PM with debby83317@gmail.com
```

---

## 📼 Demo

[![Demo](https://img.shields.io/badge/Youtube-Demo-red)](https://youtu.be/PqSUVuHGVLI)

---

## 🧠 Learnings

- Gemini function calling is more robust with clear JSON argument structures.
- OAuth2 token handling on cloud platforms requires careful permission separation.
- System is better kept on-prem or via hybrid deployment for personalized agent experiences.

---

## 🧩 Future Improvements

- Add support for Google Meet links auto-insertion
- Enable Notion → Agent reverse command sync
- Deploy as multi-agent backend with persistent context memory

---

🔐 For security, this repo excludes local `token.json`, `config.py`, and `.env` files. Please follow setup instructions to authenticate your own workspace.

## 📜 License

MIT License (c) 2025 Debby Yeh
