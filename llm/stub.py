import os
import glob
import re
import requests
from openai import OpenAI

# Fetch API key from environment
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
client = OpenAI(
    api_key=API_KEY,
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

def generate_code_for_data(task_text: str):
    prompt = (
        "You are a Python data analyst. Based on the following task description, parse the information & separate source info and analytical actions.\n"
        "Generate Python code that:\n"
        "- Detects if the source is a URL, CSV, or JSON.\n"
        "- If URL, disable SSL verification.\n"
        "- Reads the data into a pandas DataFrame.\n"
        "- Identifies column names and their types.\n"
        "- At the end, assign a dictionary of column names and types to a variable named 'result'.\n"
        f"Task: {task_text}\n\n"
        "Python Code:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return "Error: LLM failed to generate code"




