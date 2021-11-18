from sqlalchemy import create_engine

# TODO db url and logging an env var
SQLALCHEMY_DB_URL = (
    "postgresql+psycopg2://postgres:postgres@localhost:5432/rc4laundry_test"
)

engine = create_engine(SQLALCHEMY_DB_URL, echo=True)

# db for dependency injection,
# see https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
def get_db():
    with engine.connect() as connection:
        yield connection
