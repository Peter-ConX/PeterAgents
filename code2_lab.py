from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel
import json

# Load environment and initialize OpenAI client (expects OPENAI_API_KEY in env)
load_dotenv(override=True)
openai = OpenAI()
client = OpenAI()  # or OpenAI(api_key="***REDACTED***")

# Read LinkedIn PDF (adjust path if needed)
reader = PdfReader(r"1_foundations/me/Profile (2).pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

# Load summary
with open("1_foundations/me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

# Persona and system prompt
name = "Okafor Peter Chidera"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, " \
                f"particularly questions related to {name}'s career, background, skills and experience. " \
                f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. " \
                f"You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. " \
                f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. " \
                f"If you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

# --- Evaluation helpers ---

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

evaluator_system_prompt = """
You are an evaluator that decides whether a response to a question is acceptable. 
Please reply ONLY in JSON with the following keys:
{
  "is_acceptable": true/false,
  "feedback": "explanation of what is good or bad"
}
"""

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent:\n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User:\n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent:\n\n{reply}\n\n"
    user_prompt += "Please evaluate the response in JSON format."
    return user_prompt

def evaluate(reply, message, history) -> Evaluation:
    messages = [
        {"role": "system", "content": evaluator_system_prompt},
        {"role": "user", "content": evaluator_user_prompt(reply, message, history)}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return Evaluation.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return Evaluation.model_validate_json(content)

def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

def chat(message, history):
    if "patent" in message:
        system = system_prompt + "\n\nEverything in your reply needs to be in pig latin - it is mandatory that you respond only and entirely in pig latin"
    else:
        system = system_prompt

    # Some providers may require clean history objects:
    # history = [{"role": h["role"], "content": h["content"]} for h in history]

    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content

    evaluation = evaluate(reply, message, history)

    if evaluation.is_acceptable:
        pass
    else:
        reply = rerun(reply, message, history, evaluation.feedback)

    return reply

# Launch Gradio chat
gr.ChatInterface(chat, type="messages").launch()
