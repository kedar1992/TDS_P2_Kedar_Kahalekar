import pandas as pd
import requests

def execute_code2(code_str, df):
    shared_scope = {
        "__builtins__": __builtins__,
        "pd": pd,
        "requests": requests,
        "df": df  # Inject Stage-1 DataFrame
    }
    try:
        exec(code_str, shared_scope, shared_scope)
        return shared_scope.get("analysis_result", "No variable named 'analysis_result' was found.")
    except Exception as e:
        return f"Error during execution: {e}"

