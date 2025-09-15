# First let's do an import. If you get an Import Error, double check that your Kernel is correct..

from dotenv import load_dotenv

# Next it's time to load the API keys into environment variables
# If this returns false, see the next cell!

load_dotenv(override=True)

# Check the key - if you're not using OpenAI, check whichever key you're using! Ollama doesn't need a key.
# Check the key - if you're not using OpenAI, check whichever key you're using! Ollama doesn't need a key.

import os
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")


# And now - the all important import statement
# If you get an import error - head over to troubleshooting in the Setup folder
# Even for other LLM providers like Gemini, you still use this OpenAI import - see Guide 9 for why

from openai import OpenAI

# And now we'll create an instance of the OpenAI class
# If you're not sure what it means to create an instance of a class - head over to the guides folder (guide 6)!
# If you get a NameError - head over to the guides folder (guide 6)to learn about NameErrors - always instantly fixable
# If you're not using OpenAI, you just need to slightly modify this - precise instructions are in the AI APIs guide (guide 9)

openai = OpenAI()

# Create a list of messages in the familiar OpenAI format

messages = [{"role": "user", "content": "What is 2+2?"}]

# And now call it! Any problems, head to the troubleshooting guide
# This uses GPT 4.1 nano, the incredibly cheap model
# The APIs guide (guide 9) has exact instructions for using even cheaper or free alternatives to OpenAI
# If you get a NameError, head to the guides folder (guide 6) to learn about NameErrors - always instantly fixable

response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=messages
)

print(response.choices[0].message.content)

# And now - let's ask for a question:

question = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
messages = [{"role": "user", "content": question}]

# ask it - this uses GPT 4.1 mini, still cheap but more powerful than nano

response = openai.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages
)

question = response.choices[0].message.content

print(question)

# form a new messages list
message =[{"role": "user", "content":question}]

# Ask it again

response = openai.chat.completions.create(
    model = "gpt-4.1-mini",
    messages=messages
)

answer = response.choices[0].message.content
print(answer)

from IPython.display import Markdown, display

display(Markdown(answer))



# First create the messages:
import openai

messages = [{"role": "user", "content": "pick a business area that might be worth exploring for an Agentic AI opportunity."}]

# Then make the first call:

response =openai.chat.completions.create(
    model ="gpt-4.1-mini",
    messages =messages
)

# Then read the business idea:

business_idea = response.choices[0].message.content
print("Business_idea:", business_idea)

messages.append({"role": "assistant", "content": business_idea})
messages.append({"role": "user", "content": f"Present a pain-point in the {business_idea} industry that might be ripe for an Agentic solution."})

response= openai.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages
)
solution=response.choices[0].message.content
print("Agentic AI Solution:", solution)
# And repeat! In the next message, include the business idea within the message

