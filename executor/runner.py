import pandas as pd
import requests

def execute_code(code_str):
   shared_scope = {
       "__builtins__": __builtins__,
       "pd": pd,
       "requests": requests
   }
   local_vars = {}
   try:
       exec(code_str, shared_scope, shared_scope)
       return shared_scope.get("result", "No variable named 'result' was found.")
   except Exception as e:
       return f"Error during execution: {e}"
