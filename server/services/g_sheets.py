import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(dotenv_path="server/.env")

def load_sheet_data(service_account_json_path="server/services/credentials.json", spreadsheet_id = os.getenv("SHEET_ID"), sheet_range="Sheet1!A:Z"):
    """
    Loads data from a Google Sheet using a service account.

    :param service_account_json_path: Path to the service account JSON file.
    :param spreadsheet_id: The ID of the spreadsheet (found in the sheet's URL).
    :param sheet_range: The A1 notation of the range to read (e.g. 'Sheet1!A:Z').
    :return: List of rows, where each row is a list of cell values.
    """

    # Define the scope for reading data
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # Create credentials from the service account file
    credentials = service_account.Credentials.from_service_account_file(
        service_account_json_path,
        scopes=scopes
    )

    # Build the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API to get the specified range
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
    values = result.get('values', [])

    return values