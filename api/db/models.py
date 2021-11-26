import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Interval,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)

metadata_obj = MetaData()


class MachineType(str, enum.Enum):
    washer = "washer"
    dryer = "dryer"


machine = Table(
    "machine",
    metadata_obj,
    Column("id", String, primary_key=True),
    Column("floor", Integer, nullable=False),
    Column("pos", Integer, nullable=False),
    Column("is_in_use", Boolean, nullable=False),
    Column("duration", Interval, nullable=False),
    Column("last_started_at", DateTime, default=datetime.datetime(1970, 1, 1, 0, 0)),
    Column("type", Enum(MachineType)),
    UniqueConstraint("floor", "pos"),  # floor and pos must be unique pair-wise
)

api_key = Table(
    "api_key",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("api_key", String, unique=True, nullable=False),
    Column("user", String, unique=True),
)

usage_details = Table(
    "usage_details",
    metadata_obj,
    Column("machine_id", None, ForeignKey("machine.id")),
    Column("time", DateTime, nullable=False),
)

raspi = Table(
    "raspi",
    metadata_obj,
    Column("floor", Integer, unique=True, nullable=False),
    Column("ip_addr", String, unique=True, nullable=False),
)
