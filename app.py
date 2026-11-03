from agent import run_turn, system
from styles import CSS, JS, EXAMPLES
import gradio as gr


def chat(message, history):
    messages = system + history + [{"role": "user", "content": message}]
    return run_turn(messages)


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
