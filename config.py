import secrets

class Config:
    # Generates a strong random key to protect sessions and CSRF tokens
    SECRET_KEY = secrets.token_hex(32)

    # SQLite database stored locally in your project folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///exam_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- SECURE COOKIE SETTINGS ---
    SESSION_COOKIE_HTTPONLY = True   # JS cannot steal the cookie (blocks XSS)
    SESSION_COOKIE_SAMESITE = 'Lax' # Blocks cross-site request forgery
    SESSION_COOKIE_SECURE   = False  # Set True only when using HTTPS

    # CSRF protection ON for all forms
    WTF_CSRF_ENABLED = True