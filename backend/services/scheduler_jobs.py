import gc
import traceback
from extensions import db
from models import User, UserProfile
from services.gmail_service import fetch_new_emails
from services.gemini_service import process_unprocessed_emails
from services.sheets_service import sync_all_unsynced_events

def poll_all_users(app):
    """
    Background job to poll Gmail and process new emails for all connected users.
    Runs within the Flask application context passed from the main thread.
    """
    print("[SCHEDULER] Starting background polling job for all users...")
    
    total_users_processed = 0
    total_emails_fetched = 0
    total_events_created = 0
    errors = []

    with app.app_context():
        try:
            # Clean up any stale session state from previous thread runs
            db.session.remove()

            # Query users who have sync_mode active ('APP' or 'SHEETS_ONLY')
            users = User.query.join(UserProfile).filter(
                UserProfile.sync_mode.in_(["APP", "SHEETS_ONLY"])
            ).all()
            
            for user in users:
                try:
                    print(f"[SCHEDULER] Polling user: {user.email}")
                    
                    # Fetch new emails
                    fetch_res = fetch_new_emails(user)
                    fetched_count = fetch_res.get("fetched", 0)
                    fetch_errors = fetch_res.get("errors", [])
                    
                    # Process unprocessed emails to extract events
                    process_res = process_unprocessed_emails(user)
                    events_created = process_res.get("events_created", 0)

                    # Sync any newly created (unsynced) events to Google Sheets
                    # Wrapped separately so a Sheets failure never blocks Gmail/Gemini
                    sheets_synced = 0
                    try:
                        sync_res = sync_all_unsynced_events(user)
                        sheets_synced = sync_res.get("synced", 0)
                    except Exception as e_sheets:
                        error_msg = f"Sheets sync failed for {user.email}: {str(e_sheets)}"
                        print(f"[SCHEDULER] [WARN] {error_msg}")
                        errors.append(error_msg)

                    # Update counters
                    total_emails_fetched += fetched_count
                    total_events_created += events_created
                    total_users_processed += 1

                    if fetch_errors:
                        errors.extend([f"Fetch error for {user.email}: {err}" for err in fetch_errors])

                    print(f"[SCHEDULER] user={user.email} fetched={fetched_count} events_created={events_created} sheets_synced={sheets_synced}")
                    
                except Exception as e_user:
                    error_msg = f"Unexpected failure processing user {user.email}: {str(e_user)}"
                    print(f"[SCHEDULER] [ERROR] {error_msg}")
                    traceback.print_exc()
                    errors.append(error_msg)
                finally:
                    db.session.remove()

            print(f"[SCHEDULER] Finished polling job.")
            print(f"[SCHEDULER] SUMMARY: Users processed: {total_users_processed}, Emails fetched: {total_emails_fetched}, Events created: {total_events_created}, Errors: {len(errors)}")

        except Exception as e_top:
            error_msg = f"Top-level scheduler failure: {str(e_top)}"
            print(f"[SCHEDULER] [CRITICAL] {error_msg}")
            traceback.print_exc()
            errors.append(error_msg)
        finally:
            db.session.remove()
            gc.collect()
            print("[SCHEDULER] Cleaned session state and invoked explicit garbage collection.")

    return {
        "users_processed": total_users_processed,
        "emails_fetched": total_emails_fetched,
        "events_created": total_events_created,
        "errors": errors
    }
