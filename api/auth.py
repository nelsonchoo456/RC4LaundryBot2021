import uuid

from api.db.models import api_key
from sqlalchemy.connectors import Connector


def validate_api_key(c: Connector, key: str) -> bool:
    q = api_key.select().where(api_key.c.api_key == key)
    row = c.execute(q).fetchone()
    if row is None:
        return False
    return True


# create_api_key generates an api key, stores it in the database, and then returns its value
def create_api_key(c: Connector) -> str:
    new_key = str(uuid.uuid4())
    stmnt = api_key.insert().values(api_key=new_key)
    c.execute(stmnt)
    return new_key
