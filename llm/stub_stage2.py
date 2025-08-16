from openai import OpenAI
import os

# Define the API key and base URL for the proxy
# Fetch API key from environment
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://aipipe.org/openai/v1"

if not API_KEY:
    print("API key not found")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def generate_analysis_code(task_text: str) -> str:
    prompt = f"""You are a data analyst. 
        You are given a pandas DataFrame named `df`. 
        Write Python code to perform analytical tasks as per User request:
        {task_text}
        
        Strict Rules to follow:
        The only use provided dataframe df Do NOT reload or fetch data again in this code.
        If any numeric column keep the value in absolute units
        Do NOT drop rows unless explicitly asked.
        Use only the column names provided in the given dataframe Do not invent or infer any other column names.:
           - For numeric columns (int64, float64), clean values by:
             * Removing any non-numeric characters except '.' and digits
             * Remove currency symbols, commas, spaces, and footnotes; keep digits and '.'
           - For object columns that contain mixed numeric and text (e.g., '$2,923,706,026'), just keep the full numeric value and remove characters or symbols
        - If the user asks for a chart or visualization:
            * Generate the plot using matplotlib impot any required lib like matplotlib.pyplot as plt, io, base64
            * Save the figure to an in-memory buffer (BytesIO) as PNG with size <100KB.
            * Encode the image in Base64 and prefix with "data:image/png;base64,".
        Return a Python dictionary with variable name as analysis_result, with the keys based on analytical task to be performed). Do not return a list or tuple. Only return a dict with the required keys.
        Output only Python code, no explanations or comments.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return "Error: LLM failed to generate code"


