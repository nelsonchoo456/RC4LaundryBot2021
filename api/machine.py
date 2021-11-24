import datetime
from typing import List, Optional

import shortuuid
from fastapi import HTTPException, status
from pydantic import Field
from sqlalchemy.engine import Connection, Row

from api.db import models
from api.lib import BaseModel
from api.record import create_record

# metadata definition for all fields
# TODO move this somewhere more reasonable
_field_id = Field(
    default_factory=shortuuid.uuid, description="A unique ID for this machine."
)
_field_id_opt = Field(None, description=_field_id.description)
_field_floor = Field(..., description="Self explanatory.")
_field_floor_opt = Field(None, description=_field_floor.description)
_field_pos = Field(
    ...,
    description="Position of machine in the laundry room. Starts from 0 and counts from left to right.",
)
_field_pos_opt = Field(None, description=_field_pos.description)
_field_is_in_use = Field(False, description="Self explanatory.")
_field_is_in_use_opt = Field(None, description=_field_is_in_use.description)
_field_duration = Field(
    ..., description="Approximate duration, in seconds, for one cycle of this machine."
)
_field_duration_opt = Field(None, description=_field_duration.description)
_field_last_started_at = Field(
    datetime.datetime(1970, 1, 1, 0, 0, 0), description="Self explanatory."
)
_field_last_started_at_opt = Field(
    None,
    description=_field_last_started_at.description,
)
_field_type = Field(..., description="The machine is either a washer or dryer.")
_field_type_opt = Field(None, description=_field_type.description)
_field_approx_time_left = Field(
    ..., description="Approximate time remaining, in seconds, for this machine's cycle."
)
_field_approx_time_left_opt = Field(
    None, description=_field_approx_time_left.description
)


class BaseMachine(BaseModel):
    floor: int = _field_floor
    pos: int = _field_pos


class Machine(BaseMachine):
    id: str = _field_id
    is_in_use: Optional[bool] = _field_is_in_use
    duration: datetime.timedelta = _field_duration
    last_started_at: datetime.datetime = _field_last_started_at
    type: models.MachineType = _field_type


class MachineReturn(Machine):
    approx_time_left: datetime.timedelta = _field_approx_time_left

    @classmethod
    def compute_time_left(cls, start: datetime.datetime, duration: datetime.timedelta):
        return max(datetime.timedelta(0), duration - (datetime.datetime.now() - start))

    @classmethod
    def from_row(cls, row: Row):
        return cls(
            **row._asdict(),
            approx_time_left=cls.compute_time_left(row.last_started_at, row.duration),
        )

    @classmethod
    def from_machine(cls, m: Machine):
        return cls(
            **dict(m),
            approx_time_left=cls.compute_time_left(m.last_started_at, m.duration),
        )

    def to_machine(self) -> Machine:
        return Machine(**self.dict())


# Machine with all fields optional and set to None as default
class MachineOptional(BaseMachine):
    id: Optional[str] = _field_id_opt
    floor: Optional[int] = _field_floor_opt
    pos: Optional[int] = _field_pos_opt
    is_in_use: Optional[bool] = _field_is_in_use_opt
    duration: Optional[datetime.timedelta] = _field_duration_opt
    last_started_at: Optional[datetime.datetime] = _field_last_started_at_opt
    type: Optional[models.MachineType] = _field_type_opt

    class Config:
        schema_extra = {
            "example": {
                "is_in_use": True,
                "last_started_at": datetime.datetime.now(),
            }
        }


class MachineSearch(MachineOptional):
    pass


class MachineUpdate(MachineOptional):
    pass


# this class is very similar to MachinOptional, but note
# the difference in the time-related fields
class MachineFilter(BaseMachine):
    id: Optional[str] = _field_id_opt
    floor: Optional[int] = _field_floor_opt
    pos: Optional[int] = _field_pos_opt
    is_in_use: Optional[bool] = _field_is_in_use_opt
    type: Optional[models.MachineType] = _field_type_opt
    last_started_before: Optional[datetime.datetime] = Field(
        None, description="Machine should have last started before this time."
    )
    last_started_after: Optional[datetime.datetime] = Field(
        None, description="Machine should have last started after this time."
    )


def filter_machines(c: Connection, mf: MachineFilter) -> List[MachineReturn]:
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
    return MachineReturn.from_rows(res)


def search_machines(db: Connection, search: MachineSearch) -> List[MachineReturn]:
    q = models.machine.select()
    for k, v in search.dict(exclude_unset=True).items():
        q = q.where(models.machine.c[k] == v)
    res = db.execute(q)
    return MachineReturn.from_rows(res)


def create_machine(db: Connection, m: Machine) -> None:
    ins = models.machine.insert().values(**m.dict())
    db.execute(ins)


def update_machine(
    c: Connection, floor: int, pos: int, mu: MachineUpdate
) -> MachineReturn:
    if mu.is_in_use and not mu.last_started_at:
        mu.last_started_at = datetime.datetime.now()
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
        # create a record if the machine is started
        create_record(c, res.id)
    return MachineReturn.from_row(res)
