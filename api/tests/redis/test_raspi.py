import pytest
from app.raspi import RaspiFilter, RaspiIn, RaspiUpdate
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException


@pytest.fixture
def create_raspi(redis, raspi_service, mock_raspi_in):
    rj = redis.json()
    key = mock_raspi_in.create_key()
    rj.delete(key)
    raspi_service.create(mock_raspi_in)
    yield rj.get(key)
    rj.delete(key)


def test_create_raspi(create_raspi, mock_raspi_out):
    assert pytest.approx(create_raspi, jsonable_encoder(mock_raspi_out))


def test_create_dup_raspi(raspi_service, create_raspi, mock_raspi_in):
    with pytest.raises(HTTPException):
        raspi_service.create(mock_raspi_in)


def test_upsert_raspi_as_insert(redis, raspi_service):
    mock_raspi = RaspiIn(floor=11, ip_addr="133.220.202.160")
    raspi_service.upsert(mock_raspi)

    rj = redis.json()
    res = rj.get(mock_raspi.create_key())
    assert pytest.approx(res, jsonable_encoder(mock_raspi.to_raspi_out()))


def test_upsert_raspi_as_update(redis, raspi_service, mock_raspi_in):
    mock_update = RaspiIn(floor=mock_raspi_in.floor, ip_addr="200.37.8.245")
    assert mock_update != mock_raspi_in

    raspi_service.upsert(mock_update)

    rj = redis.json()
    res = rj.get(mock_update.create_key())
    assert pytest.approx(res, jsonable_encoder(mock_update))


def test_find_raspi(create_raspi, mock_raspi_out, raspi_service):
    res = raspi_service.find(RaspiFilter(floor=mock_raspi_out.floor))
    assert pytest.approx(res, [mock_raspi_out])

    res = raspi_service.find(RaspiFilter(floor=420))
    assert res == []


def test_update_raspi(create_raspi, mock_raspi_in, raspi_service):
    update = RaspiUpdate(ip_addr="38.71.225.173")
    res = raspi_service.update(mock_raspi_in.floor, update)

    assert res.ip_addr == update.ip_addr


def test_update_missing_raspi(raspi_service):
    with pytest.raises(HTTPException):
        update = RaspiUpdate(ip_addr="38.71.225.173")
        raspi_service.update(420, update)
