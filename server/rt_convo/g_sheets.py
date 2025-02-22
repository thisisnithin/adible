# If modifying these scopes, delete the file token.json.
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SHEET_ID")
SAMPLE_RANGE_NAME = "Sheet1"
