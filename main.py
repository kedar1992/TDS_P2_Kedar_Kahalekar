from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from llm.stub import generate_code_for_data
from llm.stub_stage2 import generate_analysis_code
from executor.runner import execute_code
from executor.runner_Stage2 import execute_code2
from formatter.response import format_response
import ast
import re
import numpy as np
import pandas as pd

def extract_python_code(text):
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

# test function
def make_json_serializable(obj):
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    else:
        return obj


app = FastAPI()

@app.post("/api/")
async def analyze_task(file: UploadFile = File(...)):
    task_text = await file.read()
    original_task = task_text.decode('utf-8')

    try:
        # Step 1: Generate code to read and understand data
        generated_code = generate_code_for_data(original_task)
        generated_code_data = extract_python_code(generated_code)

        # Step 2: Save generated code to file
        with open("generated_code_data.py", "w", encoding="utf-8") as f:
            f.write(generated_code_data)

        # Step 3: Validate and execute the code
        ast.parse(generated_code_data)
        print(generated_code_data)
        result = execute_code(generated_code_data)

        # Step 4: Generate analysis code
        analysis_code = generate_analysis_code(original_task, result,generated_code_data)
        analysis_code_clean = extract_python_code(analysis_code)

        with open("generated_code_analysis.py", "w", encoding="utf-8") as f:
            f.write(analysis_code_clean)

        ast.parse(analysis_code_clean)
        print(analysis_code_clean)
        analysis_result = execute_code2(analysis_code_clean)

        # Step 5: Return results
        print("Analysis Result:", analysis_result)
        response = {"Analysis_Result is-": make_json_serializable(analysis_result)}
        return JSONResponse(content=response)

    except Exception as exec_error:
        print("Execution Error:", exec_error)
        return JSONResponse(content={"error": str(exec_error)}, status_code=500)
