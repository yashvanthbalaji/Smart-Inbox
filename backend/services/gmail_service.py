import base64
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import Config
from extensions import db
from models import User, UserProfile, RawEmail

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        
    def handle_data(self, d):
        self.text.append(d)
        
    def get_data(self):
        return ''.join(self.text)

def strip_tags(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

def decode_b64url(data):
    if not data:
        return ""
    # Decodes base64url data
    decoded_bytes = base64.urlsafe_b64decode(data.encode('utf-8'))
    return decoded_bytes.decode('utf-8', errors='ignore')

def get_gmail_service(user):
    """
    Build and return a Google API client for the Gmail API using the user's UserProfile.
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
    
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(message):
    """
    Takes a Gmail API message resource and extracts the plain text body.
    """
    payload = message.get('payload', {})
    
    # 1. Direct body (not multipart)
    body_data = payload.get('body', {}).get('data')
    if body_data:
        return decode_b64url(body_data)
        
    # 2. Multipart payload
    parts = payload.get('parts', [])
    text_part = None
    html_part = None
    
    # Simple recursive function to find all text/plain or text/html parts
    def walk_parts(parts_list):
        nonlocal text_part, html_part
        for part in parts_list:
            mime_type = part.get('mimeType')
            data = part.get('body', {}).get('data')
            
            if mime_type == 'text/plain' and data:
                text_part = decode_b64url(data)
            elif mime_type == 'text/html' and data:
                html_part = decode_b64url(data)
                
            nested_parts = part.get('parts')
            if nested_parts:
                walk_parts(nested_parts)

    walk_parts(parts)
    
    if text_part:
        return text_part
    elif html_part:
        # Strip HTML tags if only HTML is found
        return strip_tags(html_part)
        
    return ""

def fetch_new_emails(user):
    """
    Fetches new emails from Gmail for the given user, parses them, and stores them in RawEmail table.
    """
    fetched_count = 0
    errors = []
    
    try:
        service = get_gmail_service(user)
        profile = user.profile
        
        # 1. Determine time window
        if profile.gmail_last_check:
            # Always look back at least 24h in case of missed runs
            min_lookback = datetime.utcnow() - timedelta(hours=24)
            start_time = min(profile.gmail_last_check, min_lookback)
        else:
            # First ever run: fetch last 7 days so no emails are missed
            start_time = datetime.utcnow() - timedelta(days=7)
            
        # Convert start_time to unix timestamp (UTC-aware conversion to timestamp)
        unix_timestamp = int(start_time.replace(tzinfo=timezone.utc).timestamp())
        
        # 2. Build search query — fetch ALL emails in window, Gemini decides relevance
        # No keyword filter: broad fetch lets AI extract events from any email
        query = f"after:{unix_timestamp} -category:promotions -category:social"
        
        # 3. Call Gmail list API
        results = service.users().messages().list(userId='me', q=query).execute()
        messages_list = results.get('messages', [])
        
        for msg_info in messages_list:
            gmail_id = msg_info.get('id')
            
            # Check if we already have this email
            existing = RawEmail.query.filter_by(gmail_id=gmail_id).first()
            if existing:
                continue
                
            try:
                # Fetch full message
                message = service.users().messages().get(userId='me', id=gmail_id, format='full').execute()
                
                # Extract headers
                headers = message.get('payload', {}).get('headers', [])
                subject = ""
                sender = ""
                date_str = ""
                
                for header in headers:
                    name = header.get('name', '').lower()
                    val = header.get('value', '')
                    if name == 'subject':
                        subject = val
                    elif name == 'from':
                        sender = val
                    elif name == 'date':
                        date_str = val
                
                # Parse Date header
                received_at = None
                if date_str:
                    try:
                        dt = parsedate_to_datetime(date_str)
                        received_at = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    except Exception as pe:
                        print(f"Error parsing date header '{date_str}': {pe}")
                        
                if not received_at:
                    internal_date_ms = message.get('internalDate')
                    if internal_date_ms:
                        received_at = datetime.utcfromtimestamp(int(internal_date_ms) / 1000.0)
                    else:
                        received_at = datetime.utcnow()
                
                # Extract body
                body = extract_email_body(message)
                
                # Create RawEmail
                raw_email = RawEmail(
                    user_id=user.id,
                    gmail_id=gmail_id,
                    sender=sender,
                    subject=subject,
                    body=body,
                    received_at=received_at,
                    processed=False
                )
                
                db.session.add(raw_email)
                fetched_count += 1
                
            except Exception as e_msg:
                err_msg = f"Error fetching message {gmail_id}: {str(e_msg)}"
                print(err_msg)
                errors.append(err_msg)
                
        # 4. Update last check timestamp to current UTC time and commit
        profile.gmail_last_check = datetime.utcnow()
        db.session.commit()
        
    except Exception as e_func:
        db.session.rollback()
        err_msg = f"Failed to fetch emails for user {user.id}: {str(e_func)}"
        print(err_msg)
        errors.append(err_msg)
        
    return {"fetched": fetched_count, "errors": errors}
