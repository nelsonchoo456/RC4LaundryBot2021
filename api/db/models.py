import datetime
import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum, Integer, Interval,
                        MetaData, Table)

metadata_obj = MetaData()


class MachineType(str, enum.Enum):
    washer = "washer"
    dryer = "dryer"


machine = Table(
    "machine",
    metadata_obj,
    Column("floor", Integer, nullable=False),
    Column("pos", Integer, nullable=False),
    Column("is_in_use", Boolean, nullable=False),
    Column("duration", Interval, nullable=False),
    Column("last_started_at", DateTime, default=datetime.datetime(1970, 1, 1, 0, 0)),
    Column("type", Enum(MachineType)),
)