# imports
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

# The usual start
load_dotenv(override=True)
openai = OpenAI()

# For pushover (set PUSHOVER_USER and PUSHOVER_TOKEN in your .env)
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_user:
    print(f"Pushover user found and starts with {pushover_user[0]}")
else:
    print("Pushover user not found")

if pushover_token:
    print(f"Pushover token found and starts with {pushover_token[0]}")
else:
    print("Pushover token not found")

def push(message: str):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

# Example push
# push("HEY!!")

def record_user_details(email: str, name: str = "Name not provided", notes: str = "not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question: str):
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional information about the conversation that's worth recording to give context"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

# IF-statement version (kept for reference)
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)

        if tool_name == "record_user_details":
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)
        else:
            result = {}

        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results

# Alternative dynamic-dispatch version (more elegant)
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results

# Load resources
reader = PdfReader("1_foundations/me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("1_foundations/me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Okafor Peter" # Change to your name

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, " \
                f"particularly questions related to {name}'s career, background, skills and experience. " \
                f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. " \
                f"You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. " \
                f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. " \
                f"If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. " \
                f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    while not done:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls":
            message_obj = response.choices[0].message
            tool_calls = message_obj.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message_obj)
            messages.extend(results)
        else:
            done = True

    return response.choices[0].message.content

# Launch Gradio chat
gr.ChatInterface(chat, type="messages").launch()
