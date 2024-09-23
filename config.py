import os

SECRET_KEY = os.getenv('SECRET_KEY', 'not-set')

SQLALCHEMY_DATABASE_URI = os.getenv('RENDER_DATABASE_URL', 'sqlite:///db.sqlite3')
