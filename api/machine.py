import datetime
from typing import Optional

from db.models import MachineType
from db.models import machine as db_machine
from fastapi import HTTPException, status
from lib import WithOptionalFields
from pydantic import BaseModel, Field
from sqlalchemy.engine import Connection, Row


class BaseMachine(BaseModel):
    # TODO refactor validation of floor and pos range
    floor: int = Field(..., ge=1, le=17, description="Which floor the machine is on.")
    pos: int = Field(
        ..., ge=0, le=3, description="Position of machine in the laundry room."
    )


# Machine DTO model, using PyDantic
class Machine(BaseMachine):
    # TODO refactor validation of floor and pos range
    floor: int = Field(..., ge=1, le=17, description="Which floor the machine is on.")
    pos: int = Field(
        ..., ge=0, le=3, description="Position of machine in the laundry room."
    )
    is_in_use: Optional[bool] = Field(
        False, description="Whether the machine is currently in use."
    )
    duration: datetime.timedelta = Field(
        ...,
        description="Approximate duration, in seconds, of one cycle for this machine.",
    )
    last_started_at: Optional[datetime.datetime] = Field(
        datetime.datetime(1970, 1, 1, 0, 0),
        description="When the machine was last started.",
    )
    type: MachineType = Field(..., description="Washer or dryer.")

    @classmethod
    def from_row(cls, row: Row):
        return Machine(**row._asdict())

    @classmethod
    def from_rows(cls, rows):
        return [Machine.from_row(row) for row in rows]


# MachineOptional is Machine with all fields as Optional
class MachineOptional(Machine, metaclass=WithOptionalFields):
    # BUG does not inherit OpenAPI metadata
    # BUG WithOptionalFields cannot affect indirect superclasses

    # Example for OpenAPI documentation
    class Config:
        schema_extra = {"example": {"floor": 14, "is_in_use": False}}


class MachineSearch(MachineOptional, metaclass=WithOptionalFields):
    pass


# MachineUpdate is Machine with all fields optional, except floor and pos
class MachineUpdate(MachineOptional):
    class Config:
        schema_extra = {
            "example": {
                "is_in_use": True,
                "last_started_at": datetime.datetime.now(),
            }
        }


class MachineFilter(BaseMachine, metaclass=WithOptionalFields):
    is_in_use: bool
    type: MachineType
    last_started_before: datetime.datetime
    last_started_after: datetime.datetime


def find_machines(c: Connection, mf: MachineFilter):
    d = mf.dict(exclude_none=True)
    q = db_machine.select()
    for k, v in d.items():
        # TODO find a smarter way to do this
        if k == "last_started_before":
            q = q.where(db_machine.c.last_started_at <= v)
            continue
        if k == "last_started_after":
            q = q.where(db_machine.c.last_started_at >= v)
            continue
        q = q.where(db_machine.c[k] == v)
    res = c.execute(q)
    return Machine.from_rows(res)


def search_machines(db: Connection, search: MachineSearch):
    q = db_machine.select()
    for k, v in search.dict(exclude_unset=True).items():
        q = q.where(db_machine.c[k] == v)
    res = db.execute(q)
    return Machine.from_rows(res)


def create_machine(db: Connection, m: Machine):
    ins = db_machine.insert().values(**m.dict())
    db.execute(ins)


def update_machine(c: Connection, floor: int, pos: int, mu: MachineUpdate):
    stmnt = (
        db_machine.update()
        .where(db_machine.c.floor == floor)
        .where(db_machine.c.pos == pos)
        .values(**mu.dict(exclude_unset=True))
        .returning("*")
    )
    res = c.execute(stmnt).fetchone()
    if not res:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Machine at floor {} position {} not found".format(floor, pos),
        )
    return Machine.from_row(res)
