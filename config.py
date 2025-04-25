# config.py


class Config:
    SECRET_KEY = "your-secret-key"  # Change this in production
    SQLALCHEMY_DATABASE_URI = "sqlite:///fintrack.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
