from bs4 import BeautifulSoup
import csv
import sys

if len(sys.argv) < 2:
    print("Usage: python3 script.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]

with open(input_file, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse HTML
soup = BeautifulSoup(html_content, "html.parser")

# Find the main table - adjust this if needed
table = soup.find("table")
if not table:
    print("No table found in the HTML.")
    exit()

# Extract headers
headers = []
header_row = table.find("thead").find("tr")
for th in header_row.find_all("th"):
    headers.append(th.get_text(strip=True))

# Extract data rows
rows = []
for tr in table.find("tbody").find_all("tr"):
    row = []
    for td in tr.find_all("td"):
        # Clean text inside cells
        text = td.get_text(strip=True).replace("\n", " ")
        row.append(text)
    rows.append(row)

# Write to CSV
with open("season_matchups.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    writer.writerows(rows)

print("✅ CSV file 'season_matchups.csv' created successfully.")
