from time import perf_counter
from datetime import datetime
import unittest

from fastapi import status
from fastapi.testclient import TestClient

from api.db.db import engine
from api.db.models import MachineType, machine, metadata_obj, record
from api.main import app
from api.tests.mocks import get_mock_machine_return, get_mock_record
from api.tests.lib import assertSameRecords

client = TestClient(app)


class TestRecord(unittest.TestCase):
    mock_washer = get_mock_machine_return(MachineType.washer, True)
    mock_dryer = get_mock_machine_return(MachineType.dryer, True)
    mock_washer_record = get_mock_record(mock_washer)
    mock_dryer_record = get_mock_record(mock_dryer)
    mock_washer_record_old = get_mock_record(
        mock_washer, datetime(2020, 11, 11, 23, 59)
    )
    mock_dryer_record_old = get_mock_record(mock_dryer, datetime(2020, 11, 11, 23, 59))

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_start = perf_counter()

    @classmethod
    def tearDownClass(cls) -> None:
        metadata_obj.drop_all(engine)

    def setUp(self) -> None:
        metadata_obj.drop_all(engine)
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
                record.insert(),
                [
                    self.mock_washer_record.to_base_record().dict(),
                    self.mock_dryer_record.to_base_record().dict(),
                    self.mock_washer_record_old.to_base_record().dict(),
                    self.mock_dryer_record_old.to_base_record().dict(),
                ],
            )

    def test_get_record(self):
        response = client.get("/record")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameRecords(
            self,
            response.json(),
            [
                self.mock_washer_record,
                self.mock_dryer_record,
                self.mock_washer_record_old,
                self.mock_dryer_record_old,
            ],
        )

    def test_get_record_with_query(self):
        # by type
        response = client.get("/record", params={"type": MachineType.dryer})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameRecords(
            self, response.json(), [self.mock_dryer_record, self.mock_dryer_record_old]
        )

        # by time, get the records from before 2021-1-1
        response = client.get("/record", params={"time_upper": datetime(2021, 1, 1)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameRecords(
            self,
            response.json(),
            [self.mock_washer_record_old, self.mock_dryer_record_old],
        )
