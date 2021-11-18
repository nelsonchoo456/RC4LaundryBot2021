import datetime
from typing import List, Optional

import machine
from db import db, models
from fastapi import Depends, FastAPI, status
from sqlalchemy.engine import Connection

# initialize database table(s), may want to move elsewhere
# to a proper init func
models.metadata_obj.create_all(db.engine)
app = FastAPI()


# TODO test this
@app.post(
    "/machine",
    status_code=status.HTTP_201_CREATED,
    description="Creates a new machine.",
)
async def create_machine(m: machine.Machine, c: Connection = Depends(db.get_db)):
    machine.create_machine(c, m)


# TODO test this
@app.post(
    "/machine/search",
    response_model=List[machine.Machine],
    description="Directly search for machines based on its attributes.",
)
async def search_machines(
    search: machine.MachineSearch, c: Connection = Depends(db.get_db)
):
    ms = machine.find_machines(c, search)  # ms should be a list of machine.Machine
    return ms


# TODO test this
@app.get(
    "/machine",
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
@app.put(
    "/machine",
    response_model=machine.Machine,
    description="Performs partial update of specified machine.",
)
async def update_machine(
    mu: machine.MachineUpdate, floor: int, pos: int, c: Connection = Depends(db.get_db)
):
    # TODO query param validation for floor and pos
    m = machine.update_machine(c, floor, pos, mu)  # should return machine.Machine
    return m
