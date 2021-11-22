import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from api.db.models import MachineType
from api.lib import FLOORS
from api.machine import Machine

from .models import machine


def insert_machines(c: Connection):
    ms = []
    for f in FLOORS:
        ms.extend(
            [
                Machine(
                    id=f"{f}:0",
                    floor=f,
                    pos=0,
                    duration=datetime.timedelta(minutes=30),
                    type=MachineType.washer,
                ).dict(),
                Machine(
                    id=f"{f}:1",
                    floor=f,
                    pos=1,
                    duration=datetime.timedelta(minutes=30),
                    type=MachineType.washer,
                ).dict(),
                Machine(
                    id=f"{f}:2",
                    floor=f,
                    pos=2,
                    duration=datetime.timedelta(minutes=40),
                    type=MachineType.dryer,
                ).dict(),
                Machine(
                    id=f"{f}:3",
                    floor=f,
                    pos=3,
                    duration=datetime.timedelta(minutes=40),
                    type=MachineType.dryer,
                ).dict(),
            ]
        )

    ins = insert(machine).values(ms).on_conflict_do_nothing()
    c.execute(ins)