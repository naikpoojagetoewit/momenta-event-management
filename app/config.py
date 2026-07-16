import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    # Falls back to local SQLite file so the project runs instantly with zero setup.
    # Set DATABASE_URL in .env to use PostgreSQL instead, e.g.:
    # postgresql://postgres:password@localhost:5432/momenta_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'momenta.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    # If mail credentials are not set, the app logs emails to console instead of sending.
    MAIL_SUPPRESS_SEND = not bool(MAIL_USERNAME and MAIL_PASSWORD)

    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    INVOICE_FOLDER = os.path.join(basedir, 'app', 'static', 'invoices')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
