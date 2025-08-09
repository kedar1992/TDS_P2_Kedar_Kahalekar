import pandas as pd
import requests
import re

source_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

def fetch_data(url):
    response = requests.get(url, verify=False)
    return response.text

data = fetch_data(source_url)
df = pd.read_html(data)[0]

df.columns = df.columns.str.strip()
df['Worldwide gross'] = df['Worldwide gross'].replace({'\$': '', ',': ''}, regex=True)
df['Worldwide gross'] = df['Worldwide gross'].str.extract('(\d+\.?\d*)')[0]
df['Worldwide gross'] = pd.to_numeric(df['Worldwide gross'], errors='coerce')

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Peak'] = pd.to_numeric(df['Peak'], errors='coerce')

analysis_result = {
    "bn_movies_before_2020": df[(df['Worldwide gross'] >= 2000) & (df['Year'] < 2020)].shape[0],
    "earliest_1_5_bn_film": df[df['Worldwide gross'] > 1500].sort_values('Year').iloc[0]['Title'],
    "correlation_rank_peak": df['Rank'].corr(df['Peak']),
    "movies_released_2017": df[df['Year'] == 2017].shape[0],
    "movies_with_peak_1": df[df['Peak'] == 1].shape[0]
}