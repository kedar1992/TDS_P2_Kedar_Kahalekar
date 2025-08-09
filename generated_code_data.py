import pandas as pd
import requests
from io import StringIO

# Define the source URL
source_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

# Function to fetch data from the URL
def fetch_data(url):
    # Disable SSL verification
    response = requests.get(url, verify=False)
    return response.text

# Fetch the data
data = fetch_data(source_url)

# Read the data into a DataFrame
df = pd.read_html(data)[0]

# Identify column names and their types
column_types = {col: df[col].dtype for col in df.columns}

# Assign the result to a variable
result = column_types