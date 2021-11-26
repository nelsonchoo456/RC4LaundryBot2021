"""Routing methods for raspi resource. All endpoints here
require a valid API token."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.engine import Connection

from api import raspi
from api.db.db import get_db
from api.raspi import Raspi, RaspiUpdate
from api.routers.lib import verify_api_key

router = APIRouter(prefix="/raspi", dependencies=[Depends(verify_api_key)])


@router.get(
    "",
    response_model=List[raspi.Raspi],
    description="Get a list of raspberry pi's deployed.",
)
def get_raspis(
    c: Connection = Depends(get_db),
    floor: Optional[int] = Query(None, description=raspi._field_floor.description),
):
    return raspi.get_raspis(c, floor)


@router.put("", status_code=status.HTTP_202_ACCEPTED, response_model=Raspi)
def update_raspi(
    *,
    c: Connection = Depends(get_db),
    floor: int = Query(..., description=raspi._field_floor.description),
    ru: RaspiUpdate
):
    return raspi.update_raspi(c, floor, ru)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_raspi(rp: Raspi, c: Connection = Depends(get_db)):
    return raspi.create_raspi(c, rp)
