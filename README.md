# Digital Twin

A Gradio chat app where visitors talk to an AI "digital twin" that answers questions about a person's career, background, skills and experience. The twin is grounded in a LinkedIn PDF export and a short written summary, and it can notify the owner by push notification when a visitor leaves contact details or asks something it can't answer.

## Files

| File | Purpose |
| --- | --- |
| `agent.py` | The agent loop shared by both interfaces. |
| `tui.py` | Terminal UI (`uv run tui.py`) that shows tool calls and the checklist live. |
| `app.py` | Gradio web chat UI (`uv run app.py`). |
| `context.py` | Builds the system prompt (`TWIN_SYSTEM_PROMPT`) from the profile data. |
| `tools.py` | Defines the tools the model can call and the code that executes them. |
| `styles.py` | Custom CSS, JavaScript and example prompts for the web UI, plus the accent colors. |

### `agent.py`
- Creates the OpenAI client (model set by `MODEL_NAME`) and the system message.
- `run_turn(messages, on_event)` runs one user turn. It calls the model, and while the `finish_reason` is `tool_calls` it runs the requested tools through `handle_tool_calls`, appends the results and calls the model again. It stops after `MAX_STEPS` iterations so it can't loop forever.
- `on_event` is an optional callback. It receives `tool_call` events (before a tool runs) and `checklist` events (after the checklist changes), which is how the TUI shows progress.

### `tui.py`
- A terminal chat built with [Rich](https://github.com/Textualize/rich). It keeps the whole conversation, including tool calls, across turns.
- Shows each tool call as a dim `●` line and redraws the checklist panel whenever the model updates it (`☐` pending, `◐` in progress, `☑` completed).
- Commands: `/clear` resets the conversation and `/exit` quits.

### `app.py`
- `chat(message, history)` builds the messages from the Gradio history and calls `run_turn`.
- When run directly, it launches a `gr.ChatInterface` titled "Digital Twin" with the custom CSS, JS, example prompts and the `Base` theme.

### `context.py`
- Extracts text from `linkedin_profile.pdf` with `pypdf` and reads `summary.txt`.
- Combines them into `TWIN_SYSTEM_PROMPT`, which tells the model to:
  - act as the person's digital twin and say so if asked;
  - stay on professional topics (career, background, skills, experience);
  - ask for an email and call the contact tool if a visitor wants to get in touch;
  - call the unknown-question tool instead of making up answers;
  - format replies in markdown.

### `tools.py`
- `push(text)` sends a notification through the [Pushover](https://pushover.net) API.
- `record_user_details(email, name, notes)` sends a push notification when a visitor wants to be contacted.
- `record_unknown_question(question)` sends a push notification when the twin can't answer a question.
- `update_checklist(items)` replaces the checklist (a list of `content` and `status` items) like Claude Code's todo list. The model uses it to plan and track requests with several parts. `get_checklist()` and `reset_checklist()` read and clear it.
- `record_user_details_json`, `record_unknown_question_json` and `update_checklist_json` are the JSON schemas that describe these functions to the model. They are collected in the `tools` list.
- `tool_map` maps tool names to Python functions.
- `handle_tool_calls(tool_calls)` parses the model's tool call arguments, runs the matching function and returns the `tool` role messages to send back to the model. If a tool raises an error, the error text is sent back to the model instead of crashing the chat.

### `styles.py`
- `EXAMPLES`: the clickable starter questions under the chat box.
- `CSS`: a dark/light theme using gold, blue and purple accents. It restyles the chat bubbles, input, buttons and examples, and hides the Gradio footer.
- `JS`: sets the page title and keeps keyboard focus on the message box, including after each reply.
- `GOLD`, `BLUE`, `PURPLE`: the accent color constants.

## Other files

- `linkedin_profile.pdf`: LinkedIn profile export used as context.
- `summary.txt`: short personal summary used as context.
- `.env`: secrets (see below). It is listed in `.gitignore`.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) to manage dependencies. Dependencies are listed in `pyproject.toml` (`openai`, `gradio`, `python-dotenv`, `pypdf`, `requests`) and pinned in `uv.lock`.

1. Install uv if you don't have it: see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
2. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=...
   PUSHOVER_USER=...
   PUSHOVER_TOKEN=...
   ```
3. Replace `linkedin_profile.pdf` and `summary.txt` with your own.
4. Run the app. uv creates a `.venv/` folder in the project, installs the dependencies and starts the app:
   ```
   uv run app.py
   ```
   Or use the terminal UI instead of the web UI:
   ```
   uv run tui.py
   ```

To add a new dependency, use `uv add <package>`. To remove one, use `uv remove <package>`.
