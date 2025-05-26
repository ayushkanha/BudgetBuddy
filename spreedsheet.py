import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
# Define scope and credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
def add_values(new_row,username="finences"):
# Authorize and open the sheet
    
    try: 
        print(new_row)
        client = gspread.authorize(creds)
        sheet = client.open(username).sheet1  # Use .worksheet('Sheet2') for others

        # Example: Write data to sheet
        sheet.append_row(new_row)
        return "data stored"
    except Exception as e:
        return f"Failed to Add values: {str(e)}"

def extract_values(n=None):
    try:
        client = gspread.authorize(creds)
        sheet = client.open("finences").sheet1
        rows = sheet.get_all_values()

        # Trim whitespace in headers
        headers = [h.strip() for h in rows[0]]
        data = [dict(zip(headers, row)) for row in rows[1:]]

        return json.dumps(data, indent=2)
 # or json.dumps(data, indent=2) for string format
    except Exception as e:
        return f"Failed to extract values: {str(e)}"
    
from datetime import datetime

# Assume 'creds' is defined elsewhere in your code for gspread authorization
def extract_values_between_dates(input_string: str):
    start_match = re.search(r"start_date:\s*([\d\-]+)", input_string)
    end_match = re.search(r"end_date:\s*([\d\-]+)", input_string)

    if not start_match or not end_match:
        return "Error: Missing start_date or end_date."

    start_date = start_match.group(1).strip()
    end_date = end_match.group(1).strip()

    try:
        # Input: YYYY-MM-DD (e.g., "2025-05-16")
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        client = gspread.authorize(creds)
        sheet = client.open("finences").sheet1
        rows = sheet.get_all_values()

        headers = [h.strip() for h in rows[0]]
        data = []

        for row in rows[1:]:
            row_data = dict(zip(headers, row))

            try:
                # Parse actual data format: DD/MM/YYYY
                row_date = datetime.strptime(row_data.get("Date", ""), "%d/%m/%Y")
                if start <= row_date <= end:
                    data.append(row_data)
            except ValueError:
                continue  # Skip rows with invalid date

        return json.dumps(data, indent=2)

    except Exception as e:
        return f"Failed to extract values: {str(e)}"