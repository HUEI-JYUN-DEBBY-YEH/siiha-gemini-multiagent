🧭 This repo contains two architectural versions of SIIHA:

1. `adk_agent_version/` – Gemini ADK 1.4.1 implementation with multi-agent routing. (**This is the active version used in this hackathon demo.**)
2. `legacy_router_version/` – Legacy version using manual function routing.

Please refer to `adk_agent_version/` for all demo references, code walkthroughs, and future development.


# 🤖 SIIHA (ADK version): A Gemini Multi-Agent System for Human-Centered Productivity

SIIHA (System for Integrating Intelligent Human Assistants) is a modular, Gemini-powered multi-agent framework built on Google ADK 1.4.1. It integrates Gmail, Calendar, and Notion into a cohesive system to streamline human-centered workflows.

## 🧩 Key Features
- ✉️ Gmail Agent: Compose and send personalized emails
- 📅 Calendar Agent: Schedule events with time parsing and attendee extraction
- 📓 Notion Agent: Log all user interactions and actions
- 🔀 Gemini Routing: Context-aware prompt-based agent invocation
- 🔐 OAuth-secured & Notion-synced for continuity

## 🧠 Core Architecture
![image](https://github.com/HUEI-JYUN-DEBBY-YEH/siiha-gemini-multiagent/blob/main/docs/siiha_adk_diagram.png)

## 💡 Sample Prompt
> "Please email my team and schedule a marketing sync next Tuesday."

Triggers:
- Gmail Agent to compose/send the message
- Calendar Agent to schedule event
- Notion Agent to log intent & actions

## 🚀 Installation
```bash
git clone https://github.com/HUEI-JYUN-DEBBY-YEH/siiha-gemini-multiagent.git
cd siiha-gemini-multiagent
pip install -r requirements.txt
```

## ▶️ Run Demo
```bash
adk web
```

## 📁 File Structure
siiha_adk/
├── agent.py            # Routing & invocation logic
├── gmail_api.py        # Gmail Agent definition
├── calendar_api.py     # Calendar Agent definition
├── notion_api.py       # Notion logging agent
├── main.py             # Entry point
├── .env                # OAuth credentials

## 🛠 Built With
- Google ADK 1.4.1
- Gemini 2.0 Flash
- Google API (Gmail / Calendar)
- Notion SDK

## 📽️ Demo Video
[![Demo](https://youtu.be/RpNZdrsccBQ?si=IlEVxv6akQotVSCt)

## 🔗 Additional Design Info
See additional_info.md for trust loop, future extensions, and technical philosophy.
