from random import randint
from datetime import datetime
from time import perf_counter
from typing import TYPE_CHECKING
from unittest import TestCase

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from api.db.db import engine
from api.db.models import MachineType, api_key, machine, metadata_obj, usage_details
from api.machine import Machine, MachineUpdate
from api.main import app
from api.tests.lib import assertSameMachines
from api.tests.mocks import get_api_key, get_mock_machine, get_mock_machine_return
from api.usage import BaseUsage

if TYPE_CHECKING:  # not sure if we need this
    from requests import Response

client = TestClient(app)


class TestMachine(TestCase):
    # washers
    mock_washer_idle: Machine = get_mock_machine_return(MachineType.washer, False)
    mock_washer_working: Machine = get_mock_machine_return(MachineType.washer, True)

    # dryers
    mock_dryer_idle: Machine = get_mock_machine_return(MachineType.dryer, False)
    mock_dryer_working: Machine = get_mock_machine_return(MachineType.dryer, True)

    # fake api keys
    good_api_key: str = get_api_key()
    bad_api_key: str = get_api_key()

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_start = perf_counter()

    @classmethod
    def tearDownClass(cls) -> None:
        metadata_obj.drop_all(engine)

    def time_since_start(self):
        return perf_counter() - self.test_start

    def setUp(self) -> None:
        metadata_obj.drop_all(engine)
        metadata_obj.create_all(engine)
        with engine.connect() as db:
            # insert some machines
            db.execute(
                machine.insert(),
                [
                    self.mock_washer_idle.dict(),
                    self.mock_washer_working.dict(),
                    self.mock_dryer_idle.dict(),
                    self.mock_dryer_working.dict(),
                ],
            )
            # and a fake api key
            db.execute(api_key.insert().values(api_key=self.good_api_key))

    def test_get_machine(self):
        response: Response = client.get("/machine")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameMachines(
            self,
            response.json(),
            [
                self.mock_dryer_idle,
                self.mock_dryer_working,
                self.mock_washer_idle,
                self.mock_washer_working,
            ],
        )

    def test_get_machine_with_query(self):
        response: Response = client.get("/machine", params={"type": "washer"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameMachines(
            self,
            response.json(),
            [
                self.mock_washer_idle,
                self.mock_washer_working,
            ],
        )

        response: Response = client.get("/machine?is_in_use=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertSameMachines(
            self,
            response.json(),
            [
                self.mock_dryer_working,
                self.mock_washer_working,
            ],
        )

    def test_create_machine_bad_api_key(self):
        m = get_mock_machine(MachineType.washer, False)

        response: Response = client.post(
            "/machine", data=m.json(), headers={"x-api-key": self.bad_api_key}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_machine_good_api_key(self):
        m = get_mock_machine(MachineType.washer, False)

        response: Response = client.post(
            "/machine", data=m.json(), headers={"x-api-key": self.good_api_key}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that the machine was actually created
        with engine.connect() as db:
            q = machine.select().where(machine.c.id == m.id)
            r = db.execute(q).fetchone()
            self.assertIsNotNone(r)
            self.assertEqual(Machine.from_row(r), m)

    def test_update_machine_bad_api_key(self):
        mu = MachineUpdate(
            is_in_use=True,
            last_started_at=datetime.now(),
        )

        response: Response = client.put(
            "/machine",
            params={
                "floor": self.mock_washer_idle.floor,
                "pos": self.mock_washer_idle.pos,
            },
            data=mu.json(),
            headers={"x-api-key": self.bad_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_machine_good_api_key(self):
        mu = MachineUpdate(
            is_in_use=True,
            last_started_at=datetime.now(),
        )

        response: Response = client.put(
            "/machine",
            params={
                "floor": self.mock_washer_idle.floor,
                "pos": self.mock_washer_idle.pos,
            },
            data=mu.json(),
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check the returned entity
        m = Machine(**response.json())
        self.assertTrue(m.is_in_use)
        self.assertAlmostEqual(
            m.last_started_at.timestamp(), datetime.now().timestamp(), delta=0.1
        )

        # and check that the database entry actually changed
        with engine.connect() as db:
            q = machine.select().where(machine.c.id == self.mock_washer_idle.id)
            r = db.execute(q).fetchone()
            self.assertIsNotNone(r)
            m = Machine.from_row(r)
            self.assertTrue(m.is_in_use)
            self.assertAlmostEqual(
                m.last_started_at.timestamp(), datetime.now().timestamp(), delta=0.1
            )

    def test_start_machine_use(self):
        # without API key
        response: Response = client.put(
            "/machine/start",
            params={
                "floor": self.mock_washer_idle.floor,
                "pos": self.mock_washer_idle.pos,
            },
            headers={"x-api-key": self.bad_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # now with the good API key
        response: Response = client.put(
            "/machine/start",
            params={
                "floor": self.mock_washer_idle.floor,
                "pos": self.mock_washer_idle.pos,
            },
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # then check that a usage record was created
        with engine.connect() as db:
            q = select(usage_details).select_from(
                usage_details.join(
                    machine,
                    machine.c.id == self.mock_washer_idle.id,
                )
            )
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
            r = BaseUsage.from_row(res)
            self.assertAlmostEqual(
                r.time.timestamp(), datetime.now().timestamp(), delta=0.1
            )

        # check that the machine is actually in use
        # and that the last_started_at is updated
        with engine.connect() as db:
            q = machine.select().where(machine.c.id == self.mock_washer_idle.id)
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
            m = Machine.from_row(res)
            self.assertTrue(m.is_in_use)
            self.assertAlmostEqual(
                m.last_started_at.timestamp(),
                datetime.now().timestamp(),
                delta=0.1,
            )

    def test_stop_machine_use(self):
        # without API key
        response: Response = client.put(
            "/machine/stop",
            params={
                "floor": self.mock_dryer_working.floor,
                "pos": self.mock_dryer_working.pos,
            },
            headers={"x-api-key": self.bad_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # now with the good API key
        response: Response = client.put(
            "/machine/stop",
            params={
                "floor": self.mock_dryer_working.floor,
                "pos": self.mock_dryer_working.pos,
            },
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # check that the machine is actually no longer in use
        # and that the last_started_at is updated
        with engine.connect() as db:
            q = machine.select().where(machine.c.id == self.mock_dryer_working.id)
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
            m = Machine.from_row(res)
            self.assertFalse(m.is_in_use)

    def test_start_stop_non_existent_machine(self):
        response: Response = client.put(
            "/machine/start",
            params={"floor": randint(6969, 696969), "pos": randint(420, 4200)},
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response: Response = client.put(
            "/machine/stop",
            params={"floor": randint(6969, 696969), "pos": randint(420, 4200)},
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
