from datetime import timedelta

import pytest
from app.config import get_settings
from app.machine import Machine, MachineStatus, MachineType
from app.raspi import RaspiIn
from app.redis.machine import MachineService
from app.redis.raspi import RaspiService
from redis import Redis


@pytest.fixture(scope="session")
def redis():
    client = Redis.from_url(get_settings().redis_test_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def machine_service(redis):
    return MachineService(redis)


@pytest.fixture(scope="session")
def raspi_service(redis):
    return RaspiService(redis)


@pytest.fixture(scope="session")
def mock_washer():
    return Machine(
        floor=14,
        pos=0,
        status=MachineStatus.idle,
        duration=timedelta(minutes=30),
        type=MachineType.washer,
    )


@pytest.fixture(scope="session")
def mock_dryer():
    return Machine(
        floor=14,
        pos=2,
        status=MachineStatus.idle,
        duration=timedelta(minutes=40),
        type=MachineType.dryer,
    )


@pytest.fixture(scope="session")
def mock_raspi_in():
    return RaspiIn(floor=14, ip_addr="165.225.55.101")


@pytest.fixture(scope="session")
def mock_raspi_out(mock_raspi_in):
    return mock_raspi_in.to_raspi_out()
