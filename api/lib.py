import inspect

import pydantic
from sqlalchemy.engine import Row


def with_optional_fields(*fields):
    """Decorator function used to modify a pydantic model's fields to all be optional.
    Alternatively, you can  also pass the field names that should be made optional as arguments
    to the decorator.
    Taken from https://github.com/samuelcolvin/pydantic/issues/1223#issuecomment-775363074
    """

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)

    return dec


class BaseModel(pydantic.BaseModel):
    @classmethod
    def from_row(cls, row: Row):
        return cls(**row._asdict())

    @classmethod
    def from_rows(cls, rows):
        return [cls.from_row(row) for row in rows]


FLOORS = [5, 8, 11, 14, 17]
