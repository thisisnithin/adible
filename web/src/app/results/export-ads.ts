"use server";

import { GoogleSpreadsheet } from "google-spreadsheet";
import { JWT } from "google-auth-library";

const SPREADSHEET_ID = "1aKFSYOadstuU0v5stSIFKzmVdii9iHkgXb-fHsFXS84";
const SPREADSHEET_SHEET_NAME = "Sheet1";

export const exportAds = async (
  result: { title: string; content: string; url: string }[],
  topics: string[]
): Promise<void> => {
  const serviceAccountAuth = new JWT({
    email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    key: process.env.GOOGLE_PRIVATE_KEY!.split(String.raw`\n`).join("\n"),
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });

  const doc = new GoogleSpreadsheet(SPREADSHEET_ID, serviceAccountAuth);

  // Load document properties and worksheets
  await doc.loadInfo();

  // Access the specific sheet by its title
  const sheet = doc.sheetsByTitle[SPREADSHEET_SHEET_NAME];
  if (!sheet) {
    throw new Error(`Sheet "${SPREADSHEET_SHEET_NAME}" not found`);
  }

  // Retrieve all rows from the sheet
  const rows = await sheet.getRows();

  // Build a map of URL -> row (using the header name "URL")
  const urlRowMap = new Map<string, any>();
  for (const row of rows) {
    if (row.get("URL")) {
      urlRowMap.set(row.get("URL"), row);
    }
  }

  // Process each ad
  for (const ad of result) {
    // Construct the row data.
    // Assumes headers: "URL", "Title", "Content", "Tags"
    const rowData = {
      URL: ad.url,
      Title: ad.title,
      Content: ad.content,
      Tags: topics.join(", "),
    };

    if (urlRowMap.has(ad.url)) {
      // If the URL exists, update the existing row.
      const existingRow = urlRowMap.get(ad.url);
      existingRow.URL = rowData.URL;
      existingRow.Title = rowData.Title;
      existingRow.Content = rowData.Content;
      existingRow.Tags = rowData.Tags;
      await existingRow.save();
    } else {
      // Otherwise, append a new row.
      await sheet.addRow(rowData);
    }
  }
};
