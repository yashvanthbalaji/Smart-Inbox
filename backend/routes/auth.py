import logging
from flask import Blueprint, request, redirect, current_app, jsonify
from flask_jwt_extended import create_access_token
from extensions import oauth, db
from models import User, UserProfile

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/google')
def google_login():
    redirect_uri = 'http://localhost:5000/api/auth/callback'
    return oauth.google.authorize_redirect(redirect_uri, access_type='offline', prompt='consent')


@auth_bp.route('/callback')
def google_callback():
    try:
        # Exchange authorization code for tokens
        token = oauth.google.authorize_access_token()
        
        # Get userinfo
        userinfo = token.get('userinfo')
        if not userinfo:
            # Fallback if userinfo isn't directly parsed
            resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
            userinfo = resp.json()
            
        email = userinfo.get('email')
        name = userinfo.get('name')
        
        if not email:
            return jsonify({"error": "Email not provided by Google"}), 400
            
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()  # Generate user.id
            
        # Check if user profile exists
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            
        # Update OAuth tokens
        profile.google_access_token = token.get('access_token')
        refresh_token = token.get('refresh_token')
        if refresh_token:
            profile.google_refresh_token = refresh_token
            
        db.session.commit()
        
        # Issue JWT access token
        jwt_token = create_access_token(identity=str(user.id))
        
        # Redirect user back to frontend with token
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        redirect_url = f"{frontend_url.rstrip('/')}/auth/success?token={jwt_token}"
        
        return redirect(redirect_url)
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in Google OAuth Callback: {str(e)}", exc_info=True)
        return jsonify({"error": "OAuth exchange failed", "details": str(e)}), 400
