import json
import re
from datetime import date as date_type, time as time_type, datetime
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from config import Config
from extensions import db
from models import RawEmail, ExtractedEvent

# Configure Gemini client at module level
genai.configure(api_key=Config.GEMINI_API_KEY)

# Print full list of available models for confirmation (non-blocking)
print("=== Available Gemini/Gemma models ===")
try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
print("=====================================")

PRIMARY_MODEL = 'models/gemini-2.0-flash'
FALLBACK_MODEL = 'models/gemini-1.5-flash'

print(f"Selected PRIMARY_MODEL: {PRIMARY_MODEL}")
print(f"Selected FALLBACK_MODEL: {FALLBACK_MODEL}")

def extract_events_from_email(subject, body):
    """
    [Legacy] Uses Gemini to extract structured events from an email's subject and body.
    """
    prompt = f"""Read this email. Extract all meetings, exams, deadlines, interviews, or reminders mentioned.
Return ONLY a JSON array, no markdown formatting, no explanation, no code fences.
Format:
[{{"title": "", "date": "YYYY-MM-DD or null", "time": "HH:MM or null", "type": "MEETING|EXAM|DEADLINE|INTERVIEW|REMINDER|OTHER", "location": "or null", "description": ""}}]
If no event is found, return an empty array [].

Subject: {subject}
Body: {body[:3000]}"""

    try:
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip markdown code fences if Gemini adds them despite instructions
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)
        raw_text = raw_text.strip()

        events = json.loads(raw_text)

        if not isinstance(events, list):
            print(f"[Gemini] Unexpected response type (not a list): {raw_text}")
            return []

        return events

    except json.JSONDecodeError as e:
        print(f"[Gemini] JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"[Gemini] Error extracting events: {e}")
        return []

def extract_events_batch(emails, model_name):
    """
    Builds a single prompt for a batch of emails and extracts events.
    'emails' is a list of dicts, each with keys: 'id', 'subject', 'body'.
    Returns a parsed list/JSON array of events by email_id, or None if parsing fails.
    """
    prompt = """You are an email event extractor.
Below is a batch of emails. Extract all meetings, exams, deadlines, interviews, or reminders mentioned.

Return ONLY a JSON array, no markdown formatting, no explanation, no code fences.
Format:
[
  {
    "email_id": <integer matching the input Email ID>,
    "events": [
      {
        "title": "<event title>",
        "date": "YYYY-MM-DD or null",
        "time": "HH:MM or null",
        "type": "MEETING|EXAM|DEADLINE|INTERVIEW|REMINDER|OTHER",
        "location": "<location or null>",
        "description": "<brief description or null>"
      }
    ]
  }
]
Each email in the input batch MUST have exactly one entry in the returned JSON array (with an empty "events" list if no events are found for that email).

Emails in this batch:
"""

    for email in emails:
        prompt += f"\n---\nEmail ID: {email['id']}\nSubject: {email['subject']}\nBody: {email['body'][:1500]}\n---\n"

    try:
        print(f"[AI] Calling {model_name} for batch extraction of {len(emails)} emails...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip markdown fences if present
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)
        raw_text = raw_text.strip()

        result = json.loads(raw_text)
        return result
    except Exception as e:
        print(f"[AI] Batch extraction failed for model {model_name}: {e}")
        return None

def validate_batch_result(result, expected_email_ids):
    """
    Validates that the batch result is structured correctly.
    """
    if not isinstance(result, list):
        print("[AI Validation] Result is not a list.")
        return False

    result_email_ids = set()
    for item in result:
        if not isinstance(item, dict):
            print("[AI Validation] Item in result list is not a dictionary.")
            return False
        
        email_id = item.get("email_id")
        if email_id is None:
            print("[AI Validation] Missing 'email_id' in item.")
            return False
        
        result_email_ids.add(int(email_id))
        
        events = item.get("events")
        if not isinstance(events, list):
            print(f"[AI Validation] 'events' for email_id {email_id} is not a list.")
            return False
            
        for event in events:
            if not isinstance(event, dict):
                print(f"[AI Validation] Event in email_id {email_id} is not a dictionary.")
                return False
            if "title" not in event or "type" not in event:
                print(f"[AI Validation] Missing required fields 'title' or 'type' in event for email_id {email_id}.")
                return False

    # Check if all expected email IDs are represented
    expected_set = set(int(eid) for eid in expected_email_ids)
    missing_ids = expected_set - result_email_ids
    if missing_ids:
        print(f"[AI Validation] Missing email IDs in result: {missing_ids}")
        return False

    return True

def process_emails_batch(emails):
    """
    Orchestrates batch extraction using PRIMARY_MODEL and falls back to FALLBACK_MODEL if validation fails.
    """
    if not emails:
        return []

    expected_email_ids = [email['id'] for email in emails]

    # Try primary model
    result = extract_events_batch(emails, PRIMARY_MODEL)
    if result is not None and validate_batch_result(result, expected_email_ids):
        print(f"[AI] Successfully extracted and validated batch using {PRIMARY_MODEL}.")
        return result

    # Try fallback model
    print(f"[AI] Validation failed or error with {PRIMARY_MODEL}. Retrying with {FALLBACK_MODEL}...")
    result = extract_events_batch(emails, FALLBACK_MODEL)
    if result is not None and validate_batch_result(result, expected_email_ids):
        print(f"[AI] Successfully extracted and validated batch using {FALLBACK_MODEL}.")
        return result

    print("[AI] Batch extraction failed validation for both primary and fallback models.")
    return None

def _parse_date(date_str):
    """Parse a YYYY-MM-DD string to a Python date, or return None."""
    if not date_str or date_str == 'null':
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def _parse_time(time_str):
    """Parse a HH:MM string to a Python time, or return None."""
    if not time_str or time_str == 'null':
        return None
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except (ValueError, TypeError):
        return None

def process_unprocessed_emails(user, batch_size=8):
    """
    Fetches unprocessed RawEmails for user, runs AI extraction in batches,
    creates ExtractedEvent rows, marks emails as processed, and commits after each batch.
    Returns a summary dict: {processed, events_created, batches}.
    """
    total_processed = 0
    total_events_created = 0
    total_batches = 0

    try:
        # Query all unprocessed emails for this user
        unprocessed = RawEmail.query.filter_by(
            user_id=user.id,
            processed=False
        ).order_by(RawEmail.received_at.asc()).all()

        if not unprocessed:
            print(f"[AI] No unprocessed emails found for user {user.id}.")
            return {"processed": 0, "events_created": 0, "batches": 0}

        print(f"[AI] Found {len(unprocessed)} unprocessed email(s) for user {user.id}. Batch size: {batch_size}.")

        # Split into chunks
        chunks = [unprocessed[i:i + batch_size] for i in range(0, len(unprocessed), batch_size)]

        for chunk_index, chunk in enumerate(chunks):
            print(f"[AI] Processing batch {chunk_index + 1}/{len(chunks)} ({len(chunk)} emails)...")

            # Build input list for process_emails_batch
            batch_input = [
                {"id": email.id, "subject": email.subject, "body": email.body}
                for email in chunk
            ]

            # Run batch AI extraction
            result = process_emails_batch(batch_input)

            if result is None:
                print(f"[AI] Batch {chunk_index + 1} failed validation on both models — skipping (emails left unprocessed).")
                continue

            # Build a lookup: email_id -> RawEmail object
            email_lookup = {email.id: email for email in chunk}

            batch_events_created = 0

            for item in result:
                email_id = int(item.get("email_id"))
                events = item.get("events", [])
                raw_email = email_lookup.get(email_id)

                if raw_email is None:
                    print(f"[AI] Warning: email_id {email_id} in result not found in chunk — skipping.")
                    continue

                for event_data in events:
                    try:
                        extracted_event = ExtractedEvent(
                            user_id=user.id,
                            raw_email_id=raw_email.id,
                            title=event_data.get("title", "Untitled"),
                            date=_parse_date(event_data.get("date")),
                            time=_parse_time(event_data.get("time")),
                            type=event_data.get("type", "OTHER"),
                            location=event_data.get("location"),
                            description=event_data.get("description"),
                            status="PENDING"
                        )
                        db.session.add(extracted_event)
                        batch_events_created += 1
                    except Exception as e_event:
                        print(f"[AI] Error creating ExtractedEvent for email_id {email_id}: {e_event}")

                # Mark email as processed
                raw_email.processed = True
                total_processed += 1

            # Commit after each chunk so partial progress is saved
            try:
                db.session.commit()
                total_events_created += batch_events_created
                total_batches += 1
                print(f"[AI] Batch {chunk_index + 1} committed: {batch_events_created} event(s) created.")
            except Exception as e_commit:
                db.session.rollback()
                print(f"[AI] DB commit failed for batch {chunk_index + 1}: {e_commit}")

    except Exception as e_top:
        print(f"[AI] Unexpected error in process_unprocessed_emails for user {user.id}: {e_top}")

    return {"processed": total_processed, "events_created": total_events_created, "batches": total_batches}
