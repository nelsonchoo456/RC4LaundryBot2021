"""Contains model definitions and CRUD methods for machines."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Protocol, abstractmethod

from pydantic import BaseModel, Field

_field_floor = Field(..., description="Self explanatory.")
_field_floor_opt = Field(None, description=_field_floor.description)
_field_pos = Field(
    ...,
    description="Position of machine in the laundry room. Starts from 0 and counts from left to right.",
)
_field_pos_opt = Field(None, description=_field_pos.description)
_field_duration = Field(
    ..., description="Approximate duration, in seconds, for one cycle of this machine."
)
_field_duration_opt = Field(None, description=_field_duration.description)
_field_last_started_at = Field(
    description="Self explanatory.", default_factory=datetime.utcnow
)
_field_last_started_at_opt = Field(
    None,
    description=_field_last_started_at.description,
)
_field_type = Field(..., description="The machine is either a washer or dryer.")
_field_type_opt = Field(None, description=_field_type.description)
_field_approx_time_left = Field(
    timedelta(0),
    description="Approximate time remaining, in seconds, for this machine's cycle.",
)
_field_approx_time_left_opt = Field(
    None, description=_field_approx_time_left.description
)
_field_status = Field(..., description="Brief status of the machine.")
_field_status_opt = Field(None, description=_field_status.description)

# Auxiliary fields
_field_last_started_before_opt = Field(
    None, description="Machine should have last started before this time."
)
_field_last_started_after_opt = Field(
    None, description="Machine should have last started after this time."
)
_field_min_duration_opt = Field(None, description="Self explanatory.")
_field_max_duration_opt = Field(None, description="Self explanatory.")


class MachineStatus(str, Enum):
    """States which a machine could be in."""

    in_use = "in_use"
    idle = "idle"
    error = "error"
    finishing = "finishing"


class MachineType(str, Enum):
    """Type of the machine."""

    washer = "washer"
    dryer = "dryer"


class _BaseMachine(BaseModel):
    """BaseMachine holds basic fields for all machine."""

    floor: int = _field_floor
    pos: int = _field_pos

    def create_key(self):
        """Creates an id by pairing the floor and pos fields."""
        return self._create_key(self.floor, self.pos)

    @staticmethod
    def _create_key(floor: int, pos: int):
        return f"machine:{floor}:{pos}"

    @classmethod
    def from_json(cls, j: str):
        return cls(**json.loads(j))


class Machine(_BaseMachine):
    """The default Machine model."""

    type: MachineType = _field_type
    status: MachineStatus = _field_status
    duration: timedelta = _field_duration
    last_started_at: datetime = _field_last_started_at

    def create_typed_key(self):
        """Creates an id by pairing the floor and pos fields, along with the machine type."""
        return f"{self.type}:{self.floor}:{self.pos}"


class _BaseMachineOptional(BaseModel):
    """A utility class with every field optional and
    defaulting to null."""

    status: Optional[MachineStatus] = _field_status_opt


class MachineUpdate(_BaseMachineOptional):
    """Model used for partial updates to Machines."""

    duration: Optional[timedelta] = _field_duration_opt
    last_started_at: Optional[datetime] = _field_last_started_at_opt


class MachineFilter(_BaseMachineOptional):
    """Model for searching machines."""

    floor: Optional[int] = _field_floor_opt
    pos: Optional[int] = _field_pos_opt
    type: Optional[MachineType] = _field_type_opt


class IMachineService(Protocol):
    """Interface contract for CRUD methods associated to machines."""

    @abstractmethod
    def create(self, m: Machine) -> None:
        pass

    @abstractmethod
    def find(self, mf: MachineFilter) -> List[Machine]:
        pass

    @abstractmethod
    def update(self, floor: int, pos: int, mu: MachineUpdate) -> Machine:
        pass

    @abstractmethod
    def delete(self, floor: int, pos: int) -> Machine:
        pass

    @abstractmethod
    def start(self, floor: int, pos: int) -> Machine:
        pass

    @abstractmethod
    def stop(self, floor: int, pos: int) -> Machine:
        pass
