import datetime
import unittest

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from api.db.db import engine
from api.db.models import MachineType, machine, metadata_obj, record
from api.machine import Machine
from api.main import app
from api.record import Record

client = TestClient(app)


class TestRecord(unittest.TestCase):

    mock_washer = Machine(
        id="1",
        floor=14,
        pos=0,
        duration=datetime.timedelta(minutes=30),
        last_started_at=datetime.datetime.now(),
        type=MachineType.washer,
        is_in_use=False,
    )

    mock_dryer = Machine(
        id="2",
        floor=6,
        pos=3,
        duration=datetime.timedelta(minutes=40),
        last_started_at=datetime.datetime.now(),
        type=MachineType.dryer,
        is_in_use=True,
    )

    mock_records = [
        Record(
            machine_id=mock_washer.id,
            time=datetime.datetime(2021, 11, 11, 23, 59, 59),
            floor=mock_washer.floor,
            pos=mock_washer.pos,
            type=mock_washer.type,
        ),
        Record(
            machine_id=mock_dryer.id,
            time=datetime.datetime(2050, 11, 20, 23, 59, 59),
            floor=mock_dryer.floor,
            pos=mock_dryer.pos,
            type=mock_dryer.type,
        ),
    ]

    def setUp(self) -> None:
        metadata_obj.create_all(engine)
        with engine.connect() as db:
            db.execute(
                machine.insert(),
                [
                    self.mock_washer.dict(),
                    self.mock_dryer.dict(),
                ],
            )
            db.execute(
                record.insert(), [r.to_base_record().dict() for r in self.mock_records]
            )

    def tearDown(self) -> None:
        metadata_obj.drop_all(engine)

    def test_get_record(self):
        response = client.get("/record")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), [jsonable_encoder(r) for r in self.mock_records]
        )

    def test_get_record_with_query(self):
        response = client.get(
            "/record", params={"time_upper": datetime.datetime(2030, 1, 1, 0, 0, 0)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [jsonable_encoder(self.mock_records[0])])
