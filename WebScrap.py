import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from io import StringIO

# Step 1: Get the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Find the GDP table
table = soup.find("table", {"class": "wikitable"})

# Step 3: Use StringIO to avoid deprecation warning
html_str = str(table)
df = pd.read_html(StringIO(html_str))[0]

# Step 4: Handle multi-level headers by flattening
if isinstance(df.columns[0], tuple):
    df.columns = [' '.join(col).strip() for col in df.columns]

# Step 5: Clean column names
df.columns = [re.sub(r'\[.*?\]', '', col).strip() for col in df.columns]

# Step 6: Clean each cell
def clean_cell(value):
    if isinstance(value, str):
        value = re.sub(r'\[.*?\]', '', value)  # Remove [1], [note], etc.
        value = value.replace(',', '').strip()  # Remove commas
    return value

df = df.applymap(clean_cell)

# Step 7: Convert numeric columns where possible
for col in df.columns[1:]:  # Skip the first column (usually country name)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ✅ Step 8: Drop rows with any null (NaN) values
df.dropna(inplace=True)

# Step 9: Save to CSV
df.to_csv("cleaned_data.csv", index=False)

print("✅ Cleaned and filtered GDP data saved as 'cleaned_data.csv'")
