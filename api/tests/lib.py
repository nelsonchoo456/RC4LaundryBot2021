from typing import Any, List
from unittest import TestCase

from fastapi.encoders import jsonable_encoder

from api.machine import Machine, MachineReturn
from api.usage import Usage


def assert_same_machines(t: TestCase, m1: List[Any], m2: List[MachineReturn]):
    """Utility function to compare a json response against a
    predefined list of MachineReturn"""
    m1, m2 = sorted(m1, key=lambda m: m["id"]), sorted(m2, key=lambda m: m.id)
    t.assertCountEqual([Machine(**m) for m in m1], [m.to_machine() for m in m2])

    # check the `approx_time_left` field
    for i, m in enumerate(m1):
        t.assertAlmostEqual(
            m["approx_time_left"],
            m2[i].approx_time_left.total_seconds(),
            delta=t.time_since_start() + 0.1,
        )


def assert_same_usages(t: TestCase, r1: List[Any], r2: List[Usage]):
    """Utility function to compare a json response against
    a predefined list of Usage."""
    t.assertCountEqual(r1, [jsonable_encoder(r) for r in r2])
