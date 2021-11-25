import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.engine import Connection

from api import machine
from api.db import models
from api.db.db import get_db
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
async def create_machine(m: machine.Machine, c: Connection = Depends(get_db)):
    machine.create_machine(c, m)


# TODO test this
@router.post(
    "/search",
    response_model=List[machine.MachineReturn],
    description="Search for machines based on its direct attributes.",
)
async def search_machines(mf: machine.MachineSearch, c: Connection = Depends(get_db)):
    ms = machine.filter_machines(c, mf)  # ms should be a list of machine.Machine
    return ms


@router.get(
    "",
    response_model=List[machine.MachineReturn],
    description="Returns a list of machines filtered by the query parameters provided.",
)
async def get_machines(
    *,
    c: Connection = Depends(get_db),
    id: Optional[str] = Query(None, description=machine._field_id.description),
    floor: Optional[int] = Query(None, description=machine._field_floor.description),
    pos: Optional[int] = Query(None, description=machine._field_pos.description),
    is_in_use: Optional[bool] = Query(
        None, description=machine._field_is_in_use.description
    ),
    type: Optional[models.MachineType] = Query(
        None, description=machine._field_type.description
    ),
    last_started_before: Optional[datetime.datetime] = Query(
        None, description="An upper bound for the time when this machine last started."
    ),
    last_started_after: Optional[datetime.datetime] = Query(
        None, description="A lower bound for the time when this machine last started."
    )
):
    return machine.filter_machines(
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
    response_model=machine.MachineReturn,
    description="Performs partial update of specified machine.",
    dependencies=[Depends(verify_api_key)],
)
async def update_machine(
    *,
    mu: machine.MachineUpdate,
    floor: int = Query(..., description=machine._field_floor.description),
    pos: int = Query(..., description=machine._field_pos.description),
    c: Connection = Depends(get_db)
):
    m = machine.update_machine(c, floor, pos, mu)  # should return machine.Machine
    return m


@router.put(
    "/start",
    description="Start this machine.",
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_machine(
    floor: int = Query(..., description=machine._field_floor.description),
    pos: int = Query(..., description=machine._field_pos.description),
    c: Connection = Depends(get_db),
):
    machine.update_machine(c, floor, pos, machine.MachineUpdate(is_in_use=True))


@router.put(
    "/stop",
    description="Stop this machine.",
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def stop_machine(
    floor: int = Query(..., description=machine._field_floor.description),
    pos: int = Query(..., description=machine._field_pos.description),
    c: Connection = Depends(get_db),
):
    machine.update_machine(c, floor, pos, machine.MachineUpdate(is_in_use=False))
