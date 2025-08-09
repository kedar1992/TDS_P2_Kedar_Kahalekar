from openai import OpenAI

# Define the API key and base URL for the proxy
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMyMDAwMTE2QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.zMwXMjQzRY5qReAa3jvzKD9lyPw0MZm2dbm-5tSfuW0"
BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def generate_analysis_code(task_text: str, schema: dict, code1: str) -> str:
    prompt = f"""
You are a data analyst. Given the following schema:
{schema}
and following code that used logic to fetch data:
{code1}
And the user request:
\"\"\"{task_text}\"\"\"

Generate Python code that:
1. Loads the data using the same logic as before.
2. For fetching URL bypass SSL validation
3. Performs the analysis as per the user request.
4. Appropriately convert column types to numeric for any requested statistical or numerical analysis. For example, convert columns to numeric where possible.
5. If any numeric column have value such as combinition of numeric and non-numeric strings then replace non-numeric elements of value with blank but don't make entire value as blank
6. Also don't drop any rows unless specifically asked
7. Handles common data quality issues such as:
   - Non-numeric values in numeric columns
   - Missing or malformed entries
   - Inconsistent formatting (e.g., currency symbols, commas)
   - Unexpected data types
8. Cleans and validates the data before performing any operations like type conversion or filtering.
   For example, remove symbols like '$' and ',' from numeric columns and filter out non-numeric entries using regex before converting to float or int.
9. Returns the result in a variable called analysis_result.
10. Do not include any explanation or comments in the code.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return "Error: LLM failed to generate code"


