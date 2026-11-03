import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from agent import run_turn, system
from styles import GOLD, BLUE, PURPLE

# The Windows default (cp1252) can't encode the checklist icons.
sys.stdout.reconfigure(encoding="utf-8")
console = Console()

CHECKLIST_ICONS = {"pending": "☐", "in_progress": "◐", "completed": "☑"}


def render_checklist(items):
    text = Text()
    for i, item in enumerate(items):
        if i:
            text.append("\n")
        icon = CHECKLIST_ICONS[item["status"]]
        if item["status"] == "completed":
            text.append(f"{icon} {item['content']}", style="dim strike")
        elif item["status"] == "in_progress":
            text.append(f"{icon} {item['content']}", style=f"bold {GOLD}")
        else:
            text.append(f"{icon} {item['content']}")
    done = sum(1 for item in items if item["status"] == "completed")
    return Panel(text, title=f"Checklist {done}/{len(items)}", title_align="left", border_style=BLUE)


def on_event(kind, **data):
    if kind == "tool_call":
        console.print(Text(f"● {data['name']}({data['arguments']})", style="dim"))
    elif kind == "checklist":
        console.print(render_checklist(data["items"]))


def main():
    console.print(Panel("Chat with the digital twin. /clear resets the conversation, /exit quits.",
                        title="Digital Twin", title_align="left", border_style=GOLD))
    messages = list(system)
    while True:
        try:
            user_input = console.input(f"[bold {GOLD}]you ›[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            break
        if user_input == "/clear":
            messages = list(system)
            console.print("[dim]Conversation cleared.[/]")
            continue

        checkpoint = len(messages)
        messages.append({"role": "user", "content": user_input})
        try:
            with console.status("[dim]thinking…[/]", spinner="dots"):
                reply = run_turn(messages, on_event)
        except Exception as e:
            del messages[checkpoint:]
            console.print(f"[bold red]Error:[/] {e}")
            continue
        console.print(Panel(Markdown(reply), title="twin", title_align="left", border_style=PURPLE))


if __name__ == "__main__":
    main()
