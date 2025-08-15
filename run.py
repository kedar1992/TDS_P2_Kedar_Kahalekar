import sys
import requests

def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py <url>")
        return

    url = sys.argv[1]

    # Load input from file (e.g., questions.txt or input.txt)
    with open("questions.txt", "r") as f:
        payload = f.read()

    # Send as plain text
    response = requests.post(url, data=payload)

    print(response.text)

if __name__ == "__main__":
    main()

