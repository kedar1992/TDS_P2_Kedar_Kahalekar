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


def generate_analysis_code(task_text: str,  code1: str) -> str:
    prompt = f"""
You are a data analyst.
Stage-1 code (for loading and cleaning data):
{code1}

User request:
{task_text}

Strict Rules to follow:
The DataFrame from Stage-1 is already available as 'df'. Do NOT reload or fetch data.
Perform the requested analysis using only df.
If any numeric column keep the value in absolute units
Put the result in a variable called analysis_result (JSON-serializable).
Output only Python code, no explanations.
Do NOT drop rows unless explicitly asked.
Use only the column names provided in the schema dictionary. Do not invent or infer any other column names.:
   - For numeric columns (int64, float64), clean values by:
     * Removing any non-numeric characters except '.' and digits.
     * Handling currency symbols, commas, spaces, and footnotes.
   - For object columns that contain mixed numeric and text (e.g., '$2,923,706,026'), extract the full numeric value without truncation.
Output only Python code, no explanations or comments.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return "Error: LLM failed to generate code"


