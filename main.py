from fastapi import FastAPI, File, UploadFile, Body, Request
from fastapi.responses import JSONResponse
from llm.stub import generate_code_for_data
from llm.stub_stage2 import generate_analysis_code
from executor.runner import execute_code
from executor.runner_Stage2 import execute_code2
from formatter.response import format_response
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import ast
import io
import re
import numpy as np
import pandas as pd

def extract_python_code(text: str) -> str:
    """
    Extract python code from a Markdown fenced block like:
    ```python
    # code...
    ```
    Falls back to raw text if no fenced block is found.
    """
    if not text:
        return ""
    m = re.search(r"```python(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # also try a generic fenced block without language hint
    m2 = re.search(r"```(.*?)```", text, re.DOTALL)
    if m2:
        return m2.group(1).strip()
    return text.strip()


def make_json_serializable(obj):
    """Convert numpy/pandas objects into plain Python types suitable for JSON."""
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    # Handle pandas dtypes
    try:
        import pandas.api.types as ptypes  # noqa
        if isinstance(obj, pd.api.extensions.ExtensionDtype):
            return str(obj)
    except Exception:
        pass
    return obj


app = FastAPI()


@app.post("/api/")
async def handle_request(request: Request):
    """
    Supports two input modes:

    1) multipart/form-data (examiner's run.py):
       - field "questions.txt" -> UploadFile (text/plain)
       - field "edges.csv"     -> UploadFile (text/csv)

    2) raw text body (backward compatibility):
       - body is the question/task text
    """
    try:
        content_type = (request.headers.get("content-type") or "").lower()
        df = None
        questions_text = ""

        if "multipart/form-data" in content_type:
            # Robustly read form-data; do not rely on Python identifiers for field names
            form = await request.form()

            # The examiner's fields include dots in their names; fetch by exact keys.
            q_file = form.get("questions.txt") or form.get("question") or form.get("questions")
            e_file = form.get("edges.csv") or form.get("edges")

            # Read questions text
            if q_file is None:
                # If the examiner changed field names, also try any single small text file heuristically
                # (optional safety net)
                for k, v in form.items():
                    if hasattr(v, "filename") and str(v.filename).endswith(".txt"):
                        q_file = v
                        break

            if q_file is not None and hasattr(q_file, "read"):
                questions_text = (await q_file.read()).decode("utf-8", errors="replace")
            else:
                # If provided as a plain text form field (rare), coerce to str
                if q_file is not None:
                    questions_text = str(q_file)

            # Read edges.csv -> DataFrame (preferred if provided)
            if e_file is None:
                for k, v in form.items():
                    if hasattr(v, "filename") and str(v.filename).endswith(".csv"):
                        e_file = v
                        break

            if e_file is not None and hasattr(e_file, "read"):
                csv_bytes = await e_file.read()
                df = pd.read_csv(io.BytesIO(csv_bytes))
        else:
            # Plain text mode: original behavior
            body = await request.body()
            questions_text = body.decode("utf-8", errors="replace")

        # If we still don't have a DataFrame, use Stage-1 LLM to generate loader code
        if df is None:
            generated_code = generate_code_for_data(questions_text)
            generated_code_data = extract_python_code(generated_code)

            # Basic sanity check of code
            ast.parse(generated_code_data)
            stage1_output = execute_code(generated_code_data)
            df = stage1_output.get("df")
            if df is None or not isinstance(df, pd.DataFrame):
                return JSONResponse(
                    status_code=500,
                    content={"error": "Stage-1 failed to produce a DataFrame named 'df'."},
                )

        # Build schema instruction for Stage-2
        column_names = list(df.columns)
        schema = {c: str(df[c].dtype) for c in column_names}

        analysis_instructions = (
            f"{questions_text}\n\n"
            f"Use ONLY these columns from df (with dtypes): {schema}\n"
            "Do not reference any other column names."
        )

        # Stage-2: Generate analysis code and execute it
        analysis_code = generate_analysis_code(analysis_instructions)
        analysis_code_clean = extract_python_code(analysis_code)
        ast.parse(analysis_code_clean)
        analysis_result = execute_code2(analysis_code_clean, df)

        # Make sure we return JSON
        return JSONResponse(content=make_json_serializable(analysis_result))

    except Exception as exec_error:
        # Log to stdout for Render logs & examiner visibility
        print("Execution Error:", exec_error)
        return JSONResponse(content={"error": str(exec_error)}, status_code=500)


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
