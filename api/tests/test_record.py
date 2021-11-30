import unittest
from datetime import datetime
from time import perf_counter

from fastapi import status
from fastapi.testclient import TestClient

from api.db.db import engine
from api.db.models import (
    MachineStatus,
    MachineType,
    machine,
    metadata_obj,
    usage_details,
)
from api.main import app
from api.tests.lib import assert_same_usages
from api.tests.mocks import get_mock_machine_return, get_mock_usage

client = TestClient(app)


class TestUsageDetails(unittest.TestCase):
    mock_washer = get_mock_machine_return(MachineType.washer, MachineStatus.idle)
    mock_dryer = get_mock_machine_return(MachineType.dryer, MachineStatus.idle)
    mock_washer_usage = get_mock_usage(mock_washer)
    mock_dryer_usage = get_mock_usage(mock_dryer)
    mock_washer_usage_old = get_mock_usage(mock_washer, datetime(2020, 11, 11, 23, 59))
    mock_dryer_usage_old = get_mock_usage(mock_dryer, datetime(2020, 11, 11, 23, 59))

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
                usage_details.insert(),
                [
                    self.mock_washer_usage.to_base_usage().dict(),
                    self.mock_dryer_usage.to_base_usage().dict(),
                    self.mock_washer_usage_old.to_base_usage().dict(),
                    self.mock_dryer_usage_old.to_base_usage().dict(),
                ],
            )

    def test_get_usage(self):
        response = client.get("/usage")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_same_usages(
            self,
            response.json(),
            [
                self.mock_washer_usage,
                self.mock_dryer_usage,
                self.mock_washer_usage_old,
                self.mock_dryer_usage_old,
            ],
        )

    def test_get_usage_with_query(self):
        # by type
        response = client.get("/usage", params={"type": MachineType.dryer})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_same_usages(
            self, response.json(), [self.mock_dryer_usage, self.mock_dryer_usage_old]
        )

        # by time, get the usage details from before 2021-1-1
        response = client.get("/usage", params={"time_upper": datetime(2021, 1, 1)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_same_usages(
            self,
            response.json(),
            [self.mock_washer_usage_old, self.mock_dryer_usage_old],
        )
