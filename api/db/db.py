import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


engine = create_engine(os.environ.get("DB_URL"), echo=False)

# db for dependency injection,
# see https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
def get_db():
    with engine.connect() as connection:
        yield connection
