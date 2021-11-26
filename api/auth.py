import shortuuid
from sqlalchemy.connectors import Connector

from api.db.models import api_key


def validate_api_key(c: Connector, key: str) -> bool:
    """validate_api_key queries the database to
    see if the provided key is valid."""
    q = api_key.select().where(api_key.c.api_key == key)
    row = c.execute(q).fetchone()
    if row is None:
        return False
    return True


def create_api_key(c: Connector, user: str = None) -> str:
    """create_api_key generates an api key, stores it in
    the database, and then returns its value"""
    new_key = shortuuid.uuid()
    stmnt = api_key.insert().values(api_key=new_key, user=user)
    c.execute(stmnt)
    return new_key
