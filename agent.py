from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls, get_checklist, reset_checklist
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL_NAME = "gpt-5.4-mini"
MAX_STEPS = 10

openai = OpenAI()

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def run_turn(messages, on_event=None):
    """Run the agent loop for one user turn.

    `messages` must end with the user's message. It is extended in place with the
    tool calls, tool results and the final assistant reply. `on_event(kind, **data)`
    is called as the loop progresses: "tool_call" (name, arguments) before a tool
    runs, and "checklist" (items) after the checklist changes.
    """
    emit = on_event or (lambda kind, **data: None)
    reset_checklist()
    for _ in range(MAX_STEPS):
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
        choice = response.choices[0]
        if choice.finish_reason != "tool_calls":
            messages.append({"role": "assistant", "content": choice.message.content})
            return choice.message.content

        tool_calls = choice.message.tool_calls
        messages.append(choice.message)
        for tool_call in tool_calls:
            if tool_call.function.name != "update_checklist":
                emit("tool_call", name=tool_call.function.name, arguments=tool_call.function.arguments)
        messages.extend(handle_tool_calls(tool_calls))
        if any(tool_call.function.name == "update_checklist" for tool_call in tool_calls):
            emit("checklist", items=get_checklist())

    reply = "Sorry, I got stuck working on that. Could you try rephrasing your request?"
    messages.append({"role": "assistant", "content": reply})
    return reply
