import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection

from api import record
from api.db.db import get_db
from api.db.models import MachineType

router = APIRouter(prefix="/record")


@router.get(
    "", response_model=List[record.Record], description="Get a list of usage records."
)
async def get_records(
    *,
    c: Connection = Depends(get_db),
    machine_id: Optional[str] = None,
    time_lower: Optional[datetime.datetime] = Query(
        None, description="Lower bound for time of use."
    ),
    time_upper: Optional[datetime.datetime] = Query(
        None, description="Upper bound for time of use."
    ),
    floor: Optional[int] = None,
    pos: Optional[int] = None,
    type: Optional[MachineType] = None,
):
    return record.find_records(
        c,
        record.RecordFilter(
            machine_id=machine_id,
            time_lower=time_lower,
            time_upper=time_upper,
            floor=floor,
            pos=pos,
            type=type,
        ),
    )
