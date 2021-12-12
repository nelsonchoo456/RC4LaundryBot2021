from datetime import datetime

import pytest
from app.machine import (
    Machine,
    MachineFilter,
    MachineStatus,
    MachineType,
    MachineUpdate,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException


@pytest.fixture
def create_washer(redis, machine_service, mock_washer):
    machine_service.create(mock_washer)
    rj = redis.json()
    key = mock_washer.create_key()
    yield rj.get(key)
    rj.delete(key)


@pytest.fixture
def create_dryer(redis, machine_service, mock_dryer):
    machine_service.create(mock_dryer)
    rj = redis.json()
    key = mock_dryer.create_key()
    yield rj.get(key)
    rj.delete(key)


def test_create_machine(create_washer, mock_washer, create_dryer, mock_dryer):
    assert create_washer == jsonable_encoder(mock_washer)
    assert create_dryer == jsonable_encoder(mock_dryer)


def test_create_dup_machine(create_washer, mock_washer, machine_service):
    with pytest.raises(HTTPException):
        machine_service.create(mock_washer)


def test_find_machine(
    machine_service, create_washer, mock_washer, create_dryer, mock_dryer
):
    res = machine_service.find(MachineFilter(floor=14))
    assert res == [mock_washer, mock_dryer]

    res = machine_service.find(MachineFilter(type=MachineType.washer))
    assert res == [mock_washer]

    res = machine_service.find(MachineFilter(status=MachineStatus.error))
    assert res == []


def test_update_machine(redis, machine_service, create_washer, create_dryer):
    rj = redis.json()

    new_w = machine_service.update(
        create_washer["floor"],
        create_washer["pos"],
        MachineUpdate(status=MachineStatus.in_use),
    )
    assert new_w.status == MachineStatus.in_use
    assert rj.get(new_w.create_key())["status"] == MachineStatus.in_use

    now = datetime.utcnow()
    new_d = machine_service.update(
        create_dryer["floor"],
        create_dryer["pos"],
        MachineUpdate(last_started_at=now),
    )
    assert new_d.last_started_at == now
    assert rj.get(new_d.create_key())["last_started_at"] == now.isoformat()


def test_start_machine(redis, machine_service, create_washer):
    rj = redis.json()
    w = Machine(**create_washer)

    machine_service.start(w.floor, w.pos)
    res = rj.get(w.create_key())
    w_updated = Machine(**res)

    assert w_updated.status == MachineStatus.in_use
    pytest.approx(datetime.utcnow(), w_updated.last_started_at)


def test_stop_machine(redis, machine_service, create_washer):
    rj = redis.json()
    w = Machine(**create_washer)

    rj.set(w.create_key(), ".status", MachineStatus.error, xx=True)

    machine_service.stop(w.floor, w.pos)
    res = rj.get(w.create_key())
    w_updated = Machine(**res)

    assert w_updated.status == MachineStatus.idle
