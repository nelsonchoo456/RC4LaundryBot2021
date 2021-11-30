from datetime import datetime, timedelta
from itertools import count

from shortuuid import uuid

from api.db.models import MachineStatus, MachineType
from api.machine import Machine, MachineReturn
from api.raspi import Raspi
from api.usage import Usage

_int_generator = count(0, 1)


def get_mock_machine(
    type: MachineType, status: MachineStatus = MachineStatus.idle
) -> Machine:
    return Machine(
        floor=next(_int_generator),
        pos=0 if type == MachineType.washer else 2,
        duration=timedelta(minutes=30)
        if type == MachineType.washer
        else timedelta(minutes=40),
        type=type,
        status=status,
        last_started_at=datetime.now() - timedelta(minutes=10)
        if status == MachineStatus.in_use
        else datetime(2021, 11, 11, 23, 59),
    )


def get_mock_machine_return(
    type: MachineType, status: MachineStatus = MachineStatus.idle
) -> MachineReturn:
    m = get_mock_machine(type, status)
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


def get_mock_pi() -> Raspi:
    return Raspi(floor=next(_int_generator), ip_addr=uuid())
