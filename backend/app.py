import os
from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, migrate, jwt, oauth
from config import Config

from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Load configuration
    app.config.from_object(Config)

    is_debug = os.environ.get('FLASK_DEBUG', 'False') == 'True' or app.debug
    app.config.update(
        SESSION_COOKIE_SAMESITE='None' if not is_debug else 'Lax',
        SESSION_COOKIE_SECURE=not is_debug,
        SESSION_COOKIE_HTTPONLY=True,
    )

    print("=== DEBUG: SECRET_KEY set:", bool(app.config.get('SECRET_KEY')))
    print("=== DEBUG: SECRET_KEY value length:", len(app.config.get('SECRET_KEY', '')))


    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Bind all extensions to the Flask app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    oauth.init_app(app)  # MUST happen before oauth.register(...)

    # Register Google OAuth client — AFTER init_app, uses app.config for credentials
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/spreadsheets'
        }
    )

    # === TEMPORARY DEBUG PRINTS ===
    print("=== DEBUG: app.py file location:", __file__)
    print("=== DEBUG: GOOGLE_CLIENT_ID loaded:", bool(app.config.get('GOOGLE_CLIENT_ID')))
    print("=== DEBUG: oauth clients registered:", list(oauth._clients.keys()) if hasattr(oauth, '_clients') else "no _clients attr")
    print("=== DEBUG: oauth.google exists right after register:", hasattr(oauth, 'google'))

    # Enable CORS for the frontend origin with credentials support
    frontend_url = app.config.get('FRONTEND_URL', 'http://localhost:5173')
    CORS(app, origins=[frontend_url], supports_credentials=True)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok"})

    # Register blueprints AFTER oauth is fully configured
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)


    # Import models to register them with SQLAlchemy
    import models

    # Ensure database tables exist automatically on startup
    with app.app_context():
        try:
            from flask_migrate import upgrade
            upgrade()
            print("[DB MIGRATION] Database schema upgraded successfully via Flask-Migrate.")
        except Exception as e:
            print(f"[DB MIGRATION] Flask-Migrate upgrade notice ({e}), running db.create_all().")
            db.create_all()
            print("[DB MIGRATION] All tables created successfully via db.create_all().")

    # Set up Background Scheduler for Gmail polling
    import atexit
    from apscheduler.schedulers.background import BackgroundScheduler
    from services.scheduler_jobs import poll_all_users

    # Guard: only run the scheduler in the main reloader process (if debug mode is active)
    # or when debug mode is entirely disabled, to avoid starting duplicate schedulers.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=poll_all_users,
            args=[app],
            trigger="interval",
            minutes=15,
            id="poll_all_users_job"
        )
        scheduler.start()
        print("[SCHEDULER] Background scheduler started successfully.")
        print(f"[SCHEDULER] Scheduled jobs: {scheduler.get_jobs()}")
        
        # Shut down the scheduler cleanly when the app process exits
        atexit.register(lambda: scheduler.shutdown())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
