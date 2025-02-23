import os
from uuid import uuid4
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def load_sheet_data(service_account_json_path="credentials.json", spreadsheet_id = os.getenv("SHEET_ID"), sheet_range="Sheet1!A:Z"):
    """
    Loads data from a Google Sheet and returns a list of dictionaries.
    :param service_account_json_path: Path to the service account JSON file.
    :param spreadsheet_id: The ID of the spreadsheet (found in the sheet's URL).
    :param sheet_range: The A1 notation of the range to read (e.g. 'Sheet1!A:Z').
    :return: List of dicts with keys: url, title, content, and tags (as list)
    """

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    credentials = service_account.Credentials.from_service_account_file(
        service_account_json_path,
        scopes=scopes
    )

    service = build('sheets', 'v4', credentials=credentials)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
    values = result.get('values', [])

    data = []
    for row in values[1:]:
        if len(row) >= 4:
            data.append({
                'url': row[1],
                'title': row[2],
                'content': row[3],
                'tags': [tag.strip() for tag in row[4].split(',')]
            })
    
    return data

def sync_sheet_to_db(cursor, service_account_json_path="credentials.json"):
    """
    Syncs Google Sheet data to the database, adding new entries
    """
    from domain.advertisement import AdvertisementDb, get_advertisements, insert_advertisement
    
    sheet_data = load_sheet_data(service_account_json_path)
    existing_ads = {ad.url: ad for ad in get_advertisements(cursor)}
    
    for entry in sheet_data:
        if entry['url'] not in existing_ads:
            new_ad = AdvertisementDb(
                id=str(uuid4()),
                url=entry['url'],
                title=entry['title'],
                content=entry['content'],
                tags=entry['tags']
            )
            insert_advertisement(cursor, new_ad)

