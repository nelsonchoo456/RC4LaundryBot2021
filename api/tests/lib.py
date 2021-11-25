from typing import Any, List
from unittest import TestCase

from fastapi.encoders import jsonable_encoder

from api.machine import Machine, MachineReturn
from api.record import Record


# compares a json response against a predefined list of MachineReturns
def assertSameMachines(t: TestCase, m1: List[Any], m2: List[MachineReturn]):
    m1, m2 = sorted(m1, key=lambda m: m["id"]), sorted(m2, key=lambda m: m.id)
    t.assertCountEqual([Machine(**m) for m in m1], [m.to_machine() for m in m2])

    # check the `approx_time_left` field
    for i, m in enumerate(m1):
        t.assertAlmostEqual(
            m["approx_time_left"],
            m2[i].approx_time_left.total_seconds(),
            delta=t.time_since_start() + 0.1,
        )


# compares json response against a predefined list of Records
def assertSameRecords(t: TestCase, r1: List[Any], r2: List[Record]):
    t.assertCountEqual(r1, [jsonable_encoder(r) for r in r2])
