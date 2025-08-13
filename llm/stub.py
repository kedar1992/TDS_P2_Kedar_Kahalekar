import os
import glob
import re
import requests
from openai import OpenAI


API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("API key not found")

# Initialize the client

client = OpenAI(
    api_key=API_KEY,
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

def generate_code_for_data(task_text: str):

    prompt = (
        "You are a Python data analyst. Based on the following task description, parse the information & seperate source info and analytical actions to be performed \n"
        "Now Next step is to generate a python code that should understand what type of source is given like given url or csv file or json file. It's its URL then disable SSL validation for safe side\n"
        "code should also be able to read data and generate dataframe out of it"
        "based on that dataframe, identify column names and their types \n"
        "give me only python code which can use source info and generate dataframe. No analytical processing or No other extra information \n"
        "At the end of your code, assign the column names and their types as a dictionary to a variable named result \n"
        f"{task_text}\n\n"
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



