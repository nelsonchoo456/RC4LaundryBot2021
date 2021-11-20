from typing import List, Optional

import pydantic
from sqlalchemy.engine import Row


class WithOptionalFields(pydantic.main.ModelMetaclass):
    def __new__(cls, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class BaseModel(pydantic.BaseModel):
    @classmethod
    def from_row(cls, row: Row):
        return cls(**row._asdict())

    @classmethod
    def from_rows(cls, rows):
        return [cls.from_row(row) for row in rows]
