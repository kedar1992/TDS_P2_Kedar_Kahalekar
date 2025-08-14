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


def generate_analysis_code(task_text: str, schema: dict, code1: str) -> str:
    prompt = f"""
You are a data analyst. Given the following schema:
{schema}
and following code that used logic to fetch data:
{code1}
And the user request:
{task_text}

Generate Python code that:
1. Loads the data from the given sourse using pandas and BeautifulSoup.
2. Use only the column names provided in the schema dictionary. Do not invent or infer any other column names.:
   - For numeric columns (int64, float64), clean values by:
     * Removing any non-numeric characters except '.' and digits.
     * Handling currency symbols, commas, spaces, and footnotes.
     * Converting to numeric with errors='coerce'.
   - For object columns that contain mixed numeric and text (e.g., '$2,923,706,026'), extract the full numeric value without truncation.
3. Do NOT drop rows unless explicitly asked.
4. If any numeric column keep the value in absolute units
5. Add validation checks:
   - Ensure numeric columns have reasonable ranges (e.g., max > 1e9 for currency).
   - Raise ValueError if parsing fails.
6. Perform the requested analysis using the cleaned data.
7. Return the results in a variable called analysis_result.
8. Output only Python code, no explanations or comments.
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


