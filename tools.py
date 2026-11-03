import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")

pushover_url = "https://api.pushover.net/1/messages.json"


def push(text):
    requests.post(
        pushover_url,
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": text,
        },
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return "OK"


def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return "OK"


CHECKLIST_STATUSES = ("pending", "in_progress", "completed")

_checklist = []


def get_checklist():
    return [dict(item) for item in _checklist]


def reset_checklist():
    _checklist.clear()


def update_checklist(items):
    """Replace the whole checklist, like Claude Code's todo list."""
    cleaned = []
    for item in items:
        status = item.get("status")
        if status not in CHECKLIST_STATUSES:
            raise ValueError(f"status must be one of {CHECKLIST_STATUSES}, got {status!r}")
        cleaned.append({"content": item["content"], "status": status})
    _checklist[:] = cleaned
    done = sum(1 for item in cleaned if item["status"] == "completed")
    return f"Checklist updated: {done}/{len(cleaned)} completed"


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

update_checklist_json = {
    "name": "update_checklist",
    "description": (
        "Create or update your checklist for a request that has several parts. "
        "Send the complete list every time. Keep at most one item in_progress, "
        "and mark items completed as soon as they are done."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "The full checklist, in order",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "A short description of the step"},
                        "status": {"type": "string", "enum": list(CHECKLIST_STATUSES)},
                    },
                    "required": ["content", "status"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": update_checklist_json},
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
    "update_checklist": update_checklist,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        if tool is None:
            result = "Unknown tool: " + tool_name
        else:
            try:
                result = tool(**arguments)
            except Exception as e:
                print(f"Tool {tool_name} failed: {e}", flush=True)
                result = f"Error calling {tool_name}: {e}"
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results
