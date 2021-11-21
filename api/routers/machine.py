import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.engine import Connection

from api import machine
from api.db import db, models
from api.routers.lib import verify_api_key

router = APIRouter(
    prefix="/machine",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Creates a new machine.",
    dependencies=[Depends(verify_api_key)],
)
async def create_machine(m: machine.Machine, c: Connection = Depends(db.get_db)):
    machine.create_machine(c, m)


# TODO test this
@router.post(
    "/search",
    response_model=List[machine.Machine],
    description="Search for machines based on its direct attributes.",
)
async def search_machines(
    mf: machine.MachineSearch, c: Connection = Depends(db.get_db)
):
    ms = machine.find_machines(c, mf)  # ms should be a list of machine.Machine
    return ms


@router.get(
    "",
    response_model=List[machine.Machine],
    description="Returns a list of machines filtered by the query parameters provided.",
)
async def get_machines(
    *,
    c: Connection = Depends(db.get_db),
    id: Optional[str] = None,
    floor: Optional[int] = None,
    pos: Optional[int] = None,
    is_in_use: Optional[bool] = None,
    type: Optional[models.MachineType] = None,
    last_started_before: Optional[datetime.datetime] = None,
    last_started_after: Optional[datetime.datetime] = None
):
    return machine.find_machines(
        c,
        machine.MachineFilter(
            id=id,
            floor=floor,
            pos=pos,
            is_in_use=is_in_use,
            type=type,
            last_started_before=last_started_before,
            last_started_after=last_started_after,
        ),
    )


@router.put(
    "",
    response_model=machine.Machine,
    description="Performs partial update of specified machine.",
    dependencies=[Depends(verify_api_key)],
)
async def update_machine(
    mu: machine.MachineUpdate, floor: int, pos: int, c: Connection = Depends(db.get_db)
):
    # TODO query param validation for floor and pos
    m = machine.update_machine(c, floor, pos, mu)  # should return machine.Machine
    return m
