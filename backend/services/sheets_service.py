import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import Config
from extensions import db

logger = logging.getLogger(__name__)


def get_sheets_service(user):
    """
    Build and return a Google API client for the Sheets API v4 using
    the user's UserProfile OAuth tokens — identical pattern to get_gmail_service().
    """
    profile = user.profile
    if not profile:
        raise ValueError(f"User {user.id} has no associated UserProfile.")

    creds = Credentials(
        token=profile.google_access_token,
        refresh_token=profile.google_refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET
    )

    return build('sheets', 'v4', credentials=creds)


def create_or_get_spreadsheet(user):
    """
    Return the Google Sheets spreadsheet ID linked to this user.
    - If user.profile.linked_sheet_id is already set, return it immediately.
    - Otherwise create a new spreadsheet titled "SmartInbox Tracker - <email>",
      persist the spreadsheet ID to user.profile.linked_sheet_id, and return it.
    """
    profile = user.profile
    if not profile:
        raise ValueError(f"User {user.id} has no associated UserProfile.")

    # Already linked — return immediately without creating a new sheet
    if profile.linked_sheet_id:
        logger.info(f"[SHEETS] User {user.email} already linked to sheet {profile.linked_sheet_id}")
        return profile.linked_sheet_id

    # Create a brand-new spreadsheet
    service = get_sheets_service(user)

    spreadsheet_body = {
        "properties": {
            "title": f"SmartInbox Tracker - {user.email}"
        }
    }

    result = service.spreadsheets().create(
        body=spreadsheet_body,
        fields="spreadsheetId"
    ).execute()

    spreadsheet_id = result.get("spreadsheetId")

    if not spreadsheet_id:
        raise RuntimeError("Google Sheets API did not return a spreadsheet ID.")

    # Persist to DB
    profile.linked_sheet_id = spreadsheet_id
    db.session.commit()

    logger.info(f"[SHEETS] Created new spreadsheet '{spreadsheet_id}' for user {user.email}")
    return spreadsheet_id


def setup_sheet_structure(user):
    """
    Writes headers, per-row Deadline Status formulas, a dropdown validation in
    column G (Your Status), and conditional formatting to the user's linked sheet.
    Safe to call multiple times — header overwrite is idempotent.
    Returns the spreadsheet_id.
    """
    spreadsheet_id = create_or_get_spreadsheet(user)
    service = get_sheets_service(user)
    spreadsheets = service.spreadsheets()

    # ── 1. Write header row ──────────────────────────────────────────────────
    header_values = [["Title", "Type", "Date", "Time", "Location", "Deadline Status", "Your Status"]]
    spreadsheets.values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1:G1",
        valueInputOption="RAW",
        body={"values": header_values}
    ).execute()
    logger.info("[SHEETS] Header row written.")

    # ── 2. Write per-row Deadline Status formulas in column F (rows 2-1000) ──
    # Formula logic:
    #   - If col G is "Completed" → "✅ Done"
    #   - Else if col C is a valid date that is < TODAY() → "⚠️ OVERDUE"
    #   - Else → "🕒 Upcoming"
    # IFERROR(DATEVALUE(Cx), TODAY()+1) safely handles empty / non-date cells.
    formulas = []
    for row in range(2, 1001):
        formula = (
            f'=IF(G{row}="Completed","✅ Done",'
            f'IF(AND(C{row}<>"",IFERROR(DATEVALUE(C{row}),TODAY()+1)<TODAY()),'
            f'"⚠️ OVERDUE","🕒 Upcoming"))'
        )
        formulas.append([formula])

    spreadsheets.values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!F2:F1000",
        valueInputOption="USER_ENTERED",
        body={"values": formulas}
    ).execute()
    logger.info("[SHEETS] Deadline Status formulas written (F2:F1000).")

    # ── 3. batchUpdate: bold header, dropdown, conditional formatting ─────────
    SHEET_ID = 0  # first sheet always has sheetId=0 on creation

    bold_header = {
        "repeatCell": {
            "range": {
                "sheetId": SHEET_ID,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": 7
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                    "backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.21},
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)"
        }
    }

    # Dropdown in column G (index 6), rows 2-1000 (0-indexed: 1-999)
    dropdown_validation = {
        "setDataValidation": {
            "range": {
                "sheetId": SHEET_ID,
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": 6,
                "endColumnIndex": 7
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Pending"},
                        {"userEnteredValue": "Completed"}
                    ]
                },
                "showCustomUi": True,
                "strict": True
            }
        }
    }

    # Conditional formatting: OVERDUE → light red background
    cf_overdue = {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": SHEET_ID,
                    "startRowIndex": 1,
                    "endRowIndex": 1000,
                    "startColumnIndex": 5,
                    "endColumnIndex": 6
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "OVERDUE"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}
                    }
                }
            },
            "index": 0
        }
    }

    # Conditional formatting: ✅ Done → light green background
    cf_done = {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": SHEET_ID,
                    "startRowIndex": 1,
                    "endRowIndex": 1000,
                    "startColumnIndex": 5,
                    "endColumnIndex": 6
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "Done"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}
                    }
                }
            },
            "index": 1
        }
    }

    spreadsheets.batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                bold_header,
                dropdown_validation,
                cf_overdue,
                cf_done
            ]
        }
    ).execute()
    logger.info("[SHEETS] batchUpdate complete: bold header, dropdown, conditional formatting applied.")

    logger.info(f"[SHEETS] Setup complete → https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
    return spreadsheet_id


def sync_event_to_sheet(user, event):
    """
    Writes a single ExtractedEvent into the first empty row (col A blank) of the sheet.
    - Columns A-E: Title, Type, Date, Time, Location
    - Column F is left alone (formula already written by setup_sheet_structure)
    - Column G (Your Status): "Completed" if event.status == "DONE", else "Pending"
    - Marks event.synced_to_sheet = True and commits.
    Returns the 1-indexed row number written to.
    """
    spreadsheet_id = create_or_get_spreadsheet(user)
    service = get_sheets_service(user)
    spreadsheets = service.spreadsheets()

    # ── Find first empty row in column A (starting at row 2) ─────────────────
    col_a = spreadsheets.values().get(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:A"
    ).execute()

    existing = col_a.get("values", [])
    # existing is a list of rows; first row is header (index 0 → row 1)
    # First data row is index 1 → row 2. Find first index >= 1 that is empty.
    next_row = len(existing) + 1  # default: one past the last filled row
    for i, row_val in enumerate(existing[1:], start=2):
        if not row_val or not row_val[0]:
            next_row = i
            break

    # ── Build row data ────────────────────────────────────────────────────────
    date_str = event.date.isoformat() if event.date else ""
    time_str = event.time.strftime("%H:%M") if event.time else ""
    location_str = event.location or ""
    status_str = "Completed" if event.status == "DONE" else "Pending"

    row_data = [[
        event.title,
        event.type,
        date_str,
        time_str,
        location_str,
        # Column F intentionally skipped (formula already there)
        # But values().update with A-E range won't touch F/G, so we write G separately
    ]]

    # Write A-E
    spreadsheets.values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Sheet1!A{next_row}:E{next_row}",
        valueInputOption="RAW",
        body={"values": row_data}
    ).execute()

    # Write G (Your Status) separately so F formula is untouched
    spreadsheets.values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Sheet1!G{next_row}",
        valueInputOption="RAW",
        body={"values": [[status_str]]}
    ).execute()

    # Mark as synced in DB
    event.synced_to_sheet = True
    db.session.commit()

    logger.info(f"[SHEETS] Synced event '{event.title}' (id={event.id}) → row {next_row}")
    return next_row


def sync_all_unsynced_events(user):
    """
    Calls setup_sheet_structure (idempotent) then syncs every ExtractedEvent
    for this user where synced_to_sheet == False.
    Returns: {"synced": count}
    """
    from models import ExtractedEvent

    # setup_sheet_structure is idempotent — safe to call every time
    setup_sheet_structure(user)

    unsynced = ExtractedEvent.query.filter_by(
        user_id=user.id,
        synced_to_sheet=False
    ).order_by(ExtractedEvent.date.asc()).all()

    synced_count = 0
    for event in unsynced:
        try:
            row = sync_event_to_sheet(user, event)
            logger.info(f"[SHEETS] Event id={event.id} written to row {row}")
            synced_count += 1
        except Exception as e:
            logger.error(f"[SHEETS] Failed to sync event id={event.id}: {e}", exc_info=True)

    logger.info(f"[SHEETS] sync_all_unsynced_events complete: {synced_count} events synced.")
    return {"synced": synced_count}
