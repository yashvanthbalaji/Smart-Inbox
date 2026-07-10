from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # One-to-one relationship to UserProfile
    profile = db.relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    
    # One-to-many relationships
    emails = db.relationship('RawEmail', back_populates='user', cascade='all, delete-orphan')
    events = db.relationship('ExtractedEvent', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    google_access_token = db.Column(db.Text, nullable=True)
    google_refresh_token = db.Column(db.Text, nullable=True)
    gmail_last_check = db.Column(db.DateTime, nullable=True)
    linked_sheet_id = db.Column(db.String(255), nullable=True)
    sync_mode = db.Column(db.String(50), nullable=False, default='APP')  # "APP" or "SHEETS_ONLY"
    
    user = db.relationship('User', back_populates='profile')

    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'


class RawEmail(db.Model):
    __tablename__ = 'raw_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    gmail_id = db.Column(db.String(255), unique=True, nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    received_at = db.Column(db.DateTime, nullable=False)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    
    user = db.relationship('User', back_populates='emails')
    events = db.relationship('ExtractedEvent', back_populates='raw_email', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RawEmail gmail_id={self.gmail_id}>'


class ExtractedEvent(db.Model):
    __tablename__ = 'extracted_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    raw_email_id = db.Column(db.Integer, db.ForeignKey('raw_emails.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=True)
    time = db.Column(db.Time, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # MEETING, EXAM, DEADLINE, INTERVIEW, REMINDER, OTHER
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='PENDING')  # PENDING, DONE, SNOOZED
    synced_to_sheet = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', back_populates='events')
    raw_email = db.relationship('RawEmail', back_populates='events')

    def __repr__(self):
        return f'<ExtractedEvent {self.title}>'
