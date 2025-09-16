import os
from datetime import timedelta

SQLALCHEMY_DATABASE_URI = 'sqlite:///app_db.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

