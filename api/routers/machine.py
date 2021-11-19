import datetime
import os
import sys
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.engine import Connection

# see https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html#case-3-importing-from-parent-directory
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
)
from api import machine
from api.db import db, models

router = APIRouter(
    prefix="/machine",
)


# TODO test this
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Creates a new machine.",
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
    mf: machine.MachineFilter, c: Connection = Depends(db.get_db)
):
    ms = machine.find_machines(c, mf)  # ms should be a list of machine.Machine
    return ms


# TODO test this
@router.get(
    "/",
    response_model=List[machine.Machine],
    description="Returns a list of machines filtered by the query parameters provided.",
)
async def get_machines(
    *,
    c: Connection = Depends(db.get_db),
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
            floor=floor,
            pos=pos,
            is_in_use=is_in_use,
            type=type,
            last_started_before=last_started_before,
            last_started_after=last_started_after,
        ),
    )


# TODO test this
@router.put(
    "/",
    response_model=machine.Machine,
    description="Performs partial update of specified machine.",
)
async def update_machine(
    mu: machine.MachineUpdate, floor: int, pos: int, c: Connection = Depends(db.get_db)
):
    # TODO query param validation for floor and pos
    m = machine.update_machine(c, floor, pos, mu)  # should return machine.Machine
    return m
