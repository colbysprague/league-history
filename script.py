from bs4 import BeautifulSoup
import csv
import sys
import os
from collections import Counter
from typing import List, Tuple

def find_all_tables(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """Find all tables in the HTML document."""
    return soup.find_all("table")

def extract_headers(table: BeautifulSoup) -> List[str]:
    """Extract headers from a table, handling both th and td in thead/tr."""
    headers = []
    
    # Try to find thead first
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
    else:
        # If no thead, try first tr
        header_row = table.find("tr")
    
    if header_row:
        # Look for th elements first, if none found, use td
        header_cells = header_row.find_all("th")
        if not header_cells:
            header_cells = header_row.find_all("td")
        
        for cell in header_cells:
            header_text = cell.get_text(strip=True).replace("\n", " ")
            headers.append(header_text)
    
    # Handle duplicate headers
    if headers:
        counter = Counter(headers)
        for i, header in enumerate(headers):
            if counter[header] > 1:
                count = counter[header]
                counter[header] -= 1
                headers[i] = f"{header}_{count}"
    
    return headers

def extract_rows(table: BeautifulSoup, header_count: int) -> List[List[str]]:
    """Extract rows from table body, handling various table structures."""
    rows = []
    
    # Try to find tbody first
    tbody = table.find("tbody")
    if tbody:
        row_elements = tbody.find_all("tr")
    else:
        # If no tbody, use all tr elements except the first one (assumed header)
        row_elements = table.find_all("tr")[1:]
    
    for tr in row_elements:
        row = []
        cells = tr.find_all(["td", "th"])  # Include both td and th cells
        
        # Clean and extract text from each cell
        for cell in cells:
            # Handle colspan
            colspan = int(cell.get('colspan', 1))
            text = cell.get_text(strip=True).replace("\n", " ")
            
            # Add the cell value colspan times
            for _ in range(colspan):
                row.append(text)
        
        # Ensure row matches header count
        if len(row) < header_count:
            row.extend([''] * (header_count - len(row)))
        elif len(row) > header_count:
            row = row[:header_count]
        
        rows.append(row)
    
    return rows

def process_html_table(input_file: str, output_file: str) -> None:
    """Process HTML file and convert table to CSV."""
    with open(input_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    tables = find_all_tables(soup)

    if not tables:
        print("❌ No tables found in the HTML.")
        sys.exit(1)

    # If multiple tables found, ask user which one to process
    if len(tables) > 1:
        print(f"Found {len(tables)} tables in the HTML file.")
        print("\nTable previews:")
        for i, table in enumerate(tables, 1):
            headers = extract_headers(table)
            print(f"\nTable {i}:")
            print(f"Headers: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
            print(f"Number of columns: {len(headers)}")
        
        while True:
            try:
                choice = int(input(f"\nWhich table would you like to convert? (1-{len(tables)}): "))
                if 1 <= choice <= len(tables):
                    table = tables[choice - 1]
                    break
                print(f"Please enter a number between 1 and {len(tables)}")
            except ValueError:
                print("Please enter a valid number")
    else:
        table = tables[0]

    # Extract headers and rows
    headers = extract_headers(table)
    if not headers:
        print("❌ No headers found in the table.")
        sys.exit(1)

    rows = extract_rows(table, len(headers))
    if not rows:
        print("❌ No data rows found in the table.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write to CSV
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ CSV file '{output_file}' created successfully.")
    print(f"   - {len(headers)} columns")
    print(f"   - {len(rows)} rows")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 script.py <input_file> <output_file>")
        print("Example: python3 script.py input/2019-teams.html csv/2019/teams.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_html_table(input_file, output_file)
