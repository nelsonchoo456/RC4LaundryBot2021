import datetime
from typing import Optional

import shortuuid
from fastapi import HTTPException, status
from pydantic import Field
from sqlalchemy.engine import Connection

from api.db import models
from api.lib import BaseModel, WithOptionalFields
from api.record import create_record


class BaseMachine(BaseModel):
    # TODO refactor validation of floor and pos range
    id: str = Field(
        default_factory=shortuuid.uuid, description="A unique ID for this machine."
    )
    floor: int = Field(..., ge=1, le=17, description="Which floor the machine is on.")
    pos: int = Field(
        ...,
        ge=0,
        le=3,
        description="Position of machine in the laundry room. Starts from 0 and counts from left to right.",
    )


# Machine DTO model, using PyDantic
class Machine(BaseMachine):
    # TODO refactor validation of floor and pos range
    id: str = Field(
        default_factory=shortuuid.uuid, description="A unique ID for this machine."
    )
    floor: int = Field(..., ge=1, le=17, description="Which floor the machine is on.")
    pos: int = Field(
        ...,
        ge=0,
        le=3,
        description="Position of machine in the laundry room. Starts from 0 and counts from left to right.",
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
        description="Time at which the machine was last started.",
    )
    type: models.MachineType = Field(..., description="Washer or dryer.")


# MachineOptional is Machine with all fields as Optional
class MachineOptional(Machine, metaclass=WithOptionalFields):
    # BUG does not inherit OpenAPI metadata
    # BUG WithOptionalFields cannot affect indirect superclasses

    # Example for OpenAPI documentation
    class Config:
        schema_extra = {"example": {"floor": 14, "is_in_use": False}}


class MachineSearch(MachineOptional, metaclass=WithOptionalFields):
    pass


# MachineUpdate is the same as MachineOptional but the default values are None
class MachineUpdate(MachineOptional):
    floor: Optional[int] = Field(
        None, ge=1, le=17, description="Which floor the machine is on."
    )
    pos: Optional[int] = Field(
        None,
        ge=0,
        le=3,
        description="Position of machine in the laundry room. Starts from 0 and counts from left to right.",
    )
    is_in_use: Optional[bool] = Field(
        None, description="Whether the machine is currently in use."
    )
    duration: Optional[datetime.timedelta] = Field(
        None,
        description="Approximate duration, in seconds, of one cycle for this machine.",
    )
    last_started_at: Optional[datetime.datetime] = Field(
        None,
        description="Time at which the machine was last started.",
    )
    type: Optional[models.MachineType] = Field(None, description="Washer or dryer.")

    class Config:
        schema_extra = {
            "example": {
                "is_in_use": True,
                "last_started_at": datetime.datetime.now(),
            }
        }


class MachineFilter(BaseMachine, metaclass=WithOptionalFields):
    # TODO add documentation for these attributes
    is_in_use: Optional[bool] = None
    type: Optional[models.MachineType] = None
    last_started_before: Optional[datetime.datetime] = None
    last_started_after: Optional[datetime.datetime] = None


def find_machines(c: Connection, mf: MachineFilter):
    d = mf.dict(exclude_none=True)
    q = models.machine.select()
    for k, v in d.items():
        # TODO find a smarter way to do this
        if k == "last_started_before":
            q = q.where(models.machine.c.last_started_at <= v)
            continue
        if k == "last_started_after":
            q = q.where(models.machine.c.last_started_at >= v)
            continue
        q = q.where(models.machine.c[k] == v)
    res = c.execute(q)
    return Machine.from_rows(res)


def search_machines(db: Connection, search: MachineSearch):
    q = models.machine.select()
    for k, v in search.dict(exclude_unset=True).items():
        q = q.where(models.machine.c[k] == v)
    res = db.execute(q)
    return Machine.from_rows(res)


def create_machine(db: Connection, m: Machine):
    ins = models.machine.insert().values(**m.dict())
    db.execute(ins)


# TODO automatically update last_started_at
def update_machine(c: Connection, floor: int, pos: int, mu: MachineUpdate):
    stmnt = (
        models.machine.update()
        .where(models.machine.c.floor == floor)
        .where(models.machine.c.pos == pos)
        .values(**mu.dict(exclude_unset=True, exclude_none=True))
        .returning("*")
    )
    res = c.execute(stmnt).fetchone()
    if not res:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Machine at floor {floor} position {pos} not found",
        )
    if mu.is_in_use:
        create_record(c, res.id)
    return Machine.from_row(res)
