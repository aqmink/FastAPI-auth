import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 30

ALGORITHM = os.getenv("ALGORITHM")

DB_USERNAME = "root"
DB_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
DB_HOST = os.getenv("MYSQL_ROOT_HOST")
DB_NAME = os.getenv("MYSQL_ROOT_PASSWORD")
