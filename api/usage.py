"""Model definitions and CRUD methods for usage records."""

import datetime
from typing import List, Optional

from pydantic import Field
from sqlalchemy import select
from sqlalchemy.engine import Connection

from api.db.models import MachineType, machine, usage_details
from api.lib import BaseModel

# TODO move these things somewhere more reasonable
_machine_id_field = Field(
    ..., description="ID of the machine associated with this usage record."
)
_machine_id_field_opt = Field(None, description=_machine_id_field.description)
_time_field = Field(..., description="Time when it was started.")
_floor_field = Field(
    ..., description="Floor of the machine associated with this usage record."
)
_floor_field_opt = Field(None, description=_floor_field.description)
_pos_field = Field(
    ..., description="Position of the machine associated with this usage record."
)
_pos_field_opt = Field(None, description=_pos_field.description)
_type_field = Field(..., description="Washer or dryer.")
_type_field_opt = Field(None, description=_type_field.description)
_time_upper_field = Field(
    ..., description="An upper bound on the time for usage records."
)
_time_lower_field = Field(
    ..., description="A lower bound on the time for usage records."
)


class BaseUsage(BaseModel):
    """BaseUsage has shared fields for all usage models. These are
    the fields which will be stored in the relataional db table."""

    machine_id: str = _machine_id_field
    time: datetime.datetime = _time_field


class Usage(BaseUsage):
    """DTO object for usage details. Carries more information on the
    machine associated with the usage record."""

    floor: int = _floor_field
    pos: int = _pos_field
    type: MachineType = _type_field

    def to_base_usage(self):
        return BaseUsage(machine_id=self.machine_id, time=self.time)


class UsageFilter(BaseModel):
    """UsageFilter is a utility model for filtering usage records."""

    machine_id: Optional[str] = _machine_id_field_opt
    time_lower: Optional[datetime.datetime] = _time_lower_field
    time_upper: Optional[datetime.datetime] = _time_upper_field
    floor: Optional[int] = _floor_field_opt
    pos: Optional[int] = _pos_field_opt
    type: Optional[MachineType] = _type_field_opt


def filter_usage(c: Connection, rf: UsageFilter) -> List[Usage]:
    """filter_usage performs one query based on the provided filter
    and returns a list of Usage objects."""
    q = select(
        usage_details.c.machine_id,
        usage_details.c.time,
        machine.c.floor,
        machine.c.pos,
        machine.c.type,
    ).select_from(
        usage_details.join(machine, machine.c.id == usage_details.c.machine_id)
    )
    for k, v in rf.dict(exclude_unset=True, exclude_none=True).items():
        if k == "time_lower":
            q = q.where(usage_details.c.time >= v)
            continue
        if k == "time_upper":
            q = q.where(usage_details.c.time <= v)
            continue
        if k == "machine_id":
            q = q.where(usage_details.c.machine_id == v)
            continue
        q = q.where(machine.c[k] == v)

    res = c.execute(q)
    return Usage.from_rows(res)


def create_usage(c: Connection, machine_id: str):
    """create_usage inserts a usage record into the database
    using the current time."""
    c.execute(
        usage_details.insert().values(
            machine_id=machine_id, time=datetime.datetime.now()
        )
    )
