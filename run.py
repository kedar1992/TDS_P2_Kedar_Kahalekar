import subprocess
import sys

url = sys.argv[1]

curl_command = [
    "curl",
    url,
    "-F", "questions.txt=@questions.txt",
    "-F", "edges.csv=@edges.csv",
]

try:
    result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error: {e.stderr}")
