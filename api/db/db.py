import os
import urllib

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

db_uri = (
    os.environ.get("TEST_DB_URI")
    if os.environ.get("RUN_ENV") == "test"
    else os.environ.get("DB_URI")
)


def parse_cdb_uri(uri):
    db_uri = urllib.parse.unquote(os.path.expandvars(uri))
    return db_uri.replace("postgresql://", "cockroachdb://").replace(
        "postgres://", "cockroachdb://"
    )


engine = create_engine(parse_cdb_uri(db_uri))


# db for dependency injection,
# see https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
def get_db():
    with engine.connect() as connection:
        yield connection
