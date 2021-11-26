from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import Field
from sqlalchemy.engine import Connection

from api.db.models import raspi
from api.lib import BaseModel

_field_floor = Field(..., description="Which floor this pi is deployed on.")
_field_floor_opt = Field(None, description=_field_floor.description)
_field_ip_addr = Field(..., description="Local IP address of this pi.")
_field_ip_addr_opt = Field(None, description=_field_ip_addr.description)


class Raspi(BaseModel):
    """Model for raspis."""

    floor: int = _field_floor
    ip_addr: str = _field_ip_addr


class RaspiOptional(BaseModel):
    """Utility class for raspis with all fields optionsl."""

    floor: int = _field_floor_opt
    ip_addr: str = _field_ip_addr_opt


class RaspiUpdate(RaspiOptional):
    """Entity used for partial updates to raspi models."""

    pass


def get_raspis(c: Connection, floor: Optional[int] = None) -> List[Raspi]:
    q = raspi.select()
    if floor is not None:
        q = q.where(raspi.c.floor == floor)
    r = c.execute(q)
    return Raspi.from_rows(r)


def create_raspi(c: Connection, rp: Raspi) -> None:
    stmnt = raspi.insert().values(**rp.dict())
    c.execute(stmnt)


def update_raspi(c: Connection, floor: int, ru: RaspiUpdate) -> Raspi:
    """Performs partial update of a raspi entry."""
    s = raspi.update().where(raspi.c.floor == floor)
    ru_dict = ru.dict(exclude_unset=True, exclude_none=True)
    s = s.values(**ru_dict).returning("*")
    r = c.execute(s).fetchone()
    if not r:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Raspberry pi at floor ${floor} not found.",
        )
    return Raspi.from_row(r)
