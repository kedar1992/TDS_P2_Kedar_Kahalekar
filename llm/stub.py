import os
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
    base_url="https://aipipe.org/openai/v1"
)

def generate_code_for_data(task_text: str):

    prompt = (
        "You are a Python data analyst. Based on the following task description, "
        "parse the information & identify source info\n"
        "Generate Python code that:\n"
        "- Detects if the source is a URL, CSV, or JSON. If URL, load securely (default TLS verification).\n"
        "- Reads the data into a pandas DataFrame named df.\n"
        "- No Analytical action is needed strictly at this point df.\n"
        "- Code should produce 1 output with variable names as df df should have read dataframe\n"
        "Output only Python code, no explanations."
        f"\nTask:\n{task_text}\n\nPython Code:"
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




