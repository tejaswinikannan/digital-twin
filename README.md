# Digital Twin

A Gradio chat app where visitors talk to an AI "digital twin" that answers questions about a person's career, background, skills and experience. The twin is grounded in a LinkedIn PDF export and a short written summary, and it can notify the owner by push notification when a visitor leaves contact details or asks something it can't answer.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Entry point. Builds the Gradio chat UI and runs the chat loop against OpenAI. |
| `context.py` | Builds the system prompt (`TWIN_SYSTEM_PROMPT`) from the profile data. |
| `tools.py` | Defines the tools the model can call and the code that executes them. |
| `styles.py` | Custom CSS, JavaScript and example prompts for the UI. |

### `app.py`
- Loads environment variables and creates the OpenAI client (model set by `MODEL_NAME`).
- `chat(message, history)` sends the system prompt, chat history and new message to the model. While the model's `finish_reason` is `tool_calls`, it runs the requested tools through `handle_tool_calls`, appends the results and calls the model again. It returns the final text reply.
- When run directly (`python app.py`), it launches a `gr.ChatInterface` titled "Digital Twin" with the custom CSS, JS, example prompts and the `Base` theme.

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
- `record_user_details_json` and `record_unknown_question_json` are the JSON schemas that describe these functions to the model. They are collected in the `tools` list.
- `tool_map` maps tool names to Python functions.
- `handle_tool_calls(tool_calls)` parses the model's tool call arguments, runs the matching function and returns the `tool` role messages to send back to the model.

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

To add a new dependency, use `uv add <package>`. To remove one, use `uv remove <package>`.
