from datetime import datetime, timedelta
from itertools import count

from shortuuid import uuid

from api.db.models import MachineType
from api.machine import Machine, MachineReturn
from api.usage import Usage

_floor_counter = count(0, 1)


def get_mock_machine(type: MachineType, is_in_use: bool) -> Machine:
    return Machine(
        floor=next(_floor_counter),
        pos=0 if type == MachineType.washer else 2,
        duration=timedelta(minutes=30)
        if type == MachineType.washer
        else timedelta(minutes=40),
        type=type,
        is_in_use=is_in_use,
        last_started_at=datetime.now() - timedelta(minutes=10)
        if is_in_use
        else datetime(2021, 11, 11, 23, 59),
    )


def get_mock_machine_return(type: MachineType, is_in_use: bool) -> MachineReturn:
    m = get_mock_machine(type, is_in_use)
    return MachineReturn.from_machine(m)


def get_mock_usage(m: Machine, time: datetime = datetime.now()) -> Usage:
    return Usage(
        machine_id=m.id,
        time=time,
        floor=m.floor,
        pos=m.pos,
        type=m.type,
    )


def get_api_key() -> str:
    return uuid()
