import json
from datetime import datetime
from typing import List, Optional, Protocol, abstractmethod

from pydantic import BaseModel, Field

_field_floor = Field(
    ..., description="Which floor the raspi is on. There is one raspi on each floor."
)
_field_floor_opt = Field(None, description=_field_floor.description)
_field_ip_addr = Field(..., description="Local IP address of the raspi.")
_field_ip_addr_opt = Field(None, description=_field_ip_addr.description)
_field_updated_at = Field(
    description="When the raspi was last updated.", default_factory=datetime.utcnow
)
_field_updated_at_opt = Field(None, description=_field_updated_at.description)


class _BaseRaspi(BaseModel):
    """Base model for all raspis."""

    floor: int = _field_floor
    ip_addr: str = _field_floor_opt

    def create_key(self):
        return self._create_key(self.floor)

    @staticmethod
    def _create_key(floor: int):
        return f"raspi:{floor}"

    @classmethod
    def from_json(cls, j: str):
        return cls(**json.loads(j))


class RaspiOut(_BaseRaspi):
    """A raspi."""

    updated_at: datetime = _field_updated_at


class RaspiIn(_BaseRaspi):
    """Model for creating Raspis."""

    def to_raspi_out(self) -> RaspiOut:
        return RaspiOut(**self.dict())


class _BaseRaspiOptional(BaseModel):
    """Utility model for raspis with every field optional."""

    ip_addr: Optional[str] = _field_ip_addr_opt


class RaspiUpdate(_BaseRaspiOptional):
    """Model for performing partial updates to raspis."""

    updated_at: Optional[datetime] = _field_updated_at_opt


class RaspiFilter(_BaseRaspiOptional):
    """Model for searching raspis."""

    floor: Optional[int] = _field_floor_opt


class IRaspiService(Protocol):
    """'Interface' declaration for the methods a raspi service should implement."""

    @abstractmethod
    def create(self, rpi: RaspiIn) -> None:
        pass

    @abstractmethod
    def upsert(self, rpi: RaspiIn) -> None:
        pass

    @abstractmethod
    def find(self, rpif: RaspiFilter) -> List[RaspiOut]:
        pass

    @abstractmethod
    def update(self, floor: int, rpiu: RaspiUpdate) -> RaspiOut:
        pass

    @abstractmethod
    def delete(self, floor: int) -> RaspiOut:
        pass
