from fastapi import FastAPI, File, UploadFile, Body, Request
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
    elif isinstance(obj, pd.api.extensions.ExtensionDtype):
        return str(obj)


app = FastAPI()


@app.post("/api/")
async def analyze_task(
    file: UploadFile = File(None),
    text: str = Body(None),
    request: Request = None
):
    try:
        if file:
            original_task = (await file.read()).decode('utf-8')
        elif text:
            original_task = text
        else:
            # Try to extract 'question' from raw JSON
            body = await request.json()
            original_task = body.get("question")

        if not original_task:
            return JSONResponse(content={"error": "No input provided"}, status_code=400)

        # Continue with your existing logic...
        # (generate_code_for_data, execute_code, etc.)

    except Exception as exec_error:
        return JSONResponse(content={"error": str(exec_error)}, status_code=500)

    
    # Continue with your existing logic using task_text

    try:
        # Step 1: Generate code to read and understand data
        generated_code = generate_code_for_data(original_task)
        generated_code_data = extract_python_code(generated_code)

        # Step 3: Validate and execute the code
        ast.parse(generated_code_data)
        print("Generated Code Data")
        print(generated_code_data)
        stage1_output = execute_code(generated_code_data)
        df = stage1_output["df"]

        column_names = list(df.columns)
        print(column_names)
        schema = {c: str(df[c].dtype) for c in column_names}
        analysis_instructions = (f"{original_task}\n\n" f"Use ONLY these columns from df (with dtypes): {schema}\n" "Do not reference any other column names.")


        # Step 4: Generate analysis code
        analysis_code = generate_analysis_code(analysis_instructions)
        analysis_code_clean = extract_python_code(analysis_code)
        print("Analysis Code Data")
        print(analysis_code_clean)
        
        ast.parse(analysis_code_clean)
        analysis_result = execute_code2(analysis_code_clean, df)

        # Step 5: Return results
        print("Analysis Result:", analysis_result)
        #response = {"Analysis_Result is-": make_json_serializable(analysis_result)}
        response = {"Analysis_Result is-": analysis_result}
        # response = {"Schema is ": make_json_serializable(result),"code is -": generated_code_data}

        return JSONResponse(content=analysis_result)

    except Exception as exec_error:
        print("Execution Error:", exec_error)
        return JSONResponse(content={"error": str(exec_error)}, status_code=500)

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

