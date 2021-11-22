import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


DB_URL = (
    os.environ.get("TEST_DB_URL")
    if os.environ.get("RUN_ENV") == "test"
    else os.environ.get("DB_URL")
)
engine = create_engine(DB_URL)

# db for dependency injection,
# see https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
def get_db():
    with engine.connect() as connection:
        yield connection
