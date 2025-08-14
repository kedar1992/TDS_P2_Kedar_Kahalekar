import pandas as pd
import requests

def execute_code(code_str):
    shared_scope = {
        "__builtins__": __builtins__,
        "pd": pd,
        "requests": requests
    }
    try:
        exec(code_str, shared_scope, shared_scope)
        return {
            "schema": shared_scope.get("result"),
            "df": shared_scope.get("df")
        }
    except Exception as e:
        return {"error": f"Error during execution: {e}"}

