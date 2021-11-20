import datetime
from typing import Optional

from pydantic import Field
from sqlalchemy import select
from sqlalchemy.engine import Connection

from api.db.models import MachineType, machine, record
from api.lib import BaseModel


class BaseRecord(BaseModel):
    machine_id: str = Field(
        ..., description="ID of the machine associated with this usage record."
    )
    time: datetime.datetime = Field(..., description="Time of this usage.")


class Record(BaseRecord):
    floor: int = Field(
        ..., description="Floor of the machine associated with this usage record."
    )
    pos: int = Field(
        ..., description="Position of the machine associated with this usage record."
    )
    type: MachineType = Field(..., description="Washer or dryer.")

    def to_base_record(self):
        return BaseRecord(machine_id=self.machine_id, time=self.time)


# RecordFilter is used for querying records
class RecordFilter(BaseModel):
    # TODO code dupliation here, once again, as in machine.Machine too
    machine_id: Optional[str]
    time_lower: Optional[datetime.datetime]
    time_upper: Optional[datetime.datetime]
    floor: Optional[int]
    pos: Optional[int]
    type: Optional[MachineType]


def find_records(c: Connection, rf: RecordFilter):
    q = select(
        record.c.machine_id,
        record.c.time,
        machine.c.floor,
        machine.c.pos,
        machine.c.type,
    ).select_from(record.join(machine, machine.c.id == record.c.machine_id))
    for k, v in rf.dict(exclude_unset=True, exclude_none=True).items():
        if k == "time_lower":
            q = q.where(record.c.time >= v)
            continue
        if k == "time_upper":
            q = q.where(record.c.time <= v)
            continue
        if k == "machine_id":
            q = q.where(record.c.machine_id == v)
            continue
        q = q.where(machine.c[k] == v)

    res = c.execute(q)
    return Record.from_rows(res)


def create_record(c: Connection, machine_id: str):
    c.execute(
        record.insert().values(machine_id=machine_id, time=datetime.datetime.now())
    )
