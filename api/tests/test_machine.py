import datetime
import unittest
from typing import TYPE_CHECKING

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from api.db.db import engine
from api.db.models import MachineType, api_key, machine, metadata_obj, record
from api.machine import Machine, MachineUpdate
from api.main import app
from api.record import BaseRecord, Record

if TYPE_CHECKING:  # not sure if we need this
    from requests import Response

client = TestClient(app)


class TestMachine(unittest.TestCase):
    mock_washer = Machine(
        floor=14,
        pos=0,
        duration=datetime.timedelta(minutes=30),
        last_started_at=datetime.datetime.now(),
        type=MachineType.washer,
        is_in_use=False,
    )

    mock_dryer = Machine(
        floor=6,
        pos=3,
        duration=datetime.timedelta(minutes=40),
        last_started_at=datetime.datetime.now(),
        type=MachineType.dryer,
        is_in_use=True,
    )

    def setUp(self) -> None:
        metadata_obj.create_all(engine)
        with engine.connect() as db:
            # insert some machines
            db.execute(
                machine.insert(),
                [
                    self.mock_washer.dict(),
                    self.mock_dryer.dict(),
                ],
            )
            db.execute(api_key.insert().values(api_key="good-api-key"))

    def tearDown(self) -> None:
        metadata_obj.drop_all(engine)

    def test_get_machine(self):
        response: Response = client.get("/machine")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            [jsonable_encoder(self.mock_washer), jsonable_encoder(self.mock_dryer)],
        )

    def test_get_machine_with_query(self):
        response: Response = client.get("/machine", params={"type": "washer"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [jsonable_encoder(self.mock_washer)])

        response: Response = client.get("/machine?is_in_use=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [jsonable_encoder(self.mock_dryer)])

    def test_create_machine_bad_api_key(self):
        m = Machine(
            floor=17,
            pos=1,
            type=MachineType.washer,
            duration=datetime.timedelta(minutes=30),
        )

        response: Response = client.post(
            "/machine", data=m.json(), headers={"x-api-key": "bad-api-key"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_machine_good_api_key(self):
        m = Machine(
            floor=17,
            pos=1,
            type=MachineType.washer,
            duration=datetime.timedelta(minutes=30),
        )

        response: Response = client.post(
            "/machine", data=m.json(), headers={"x-api-key": "good-api-key"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that the machine was actually created
        with engine.connect() as db:
            q = machine.select().where(machine.c.floor == 17)
            r = db.execute(q).fetchone()
            self.assertIsNotNone(r)
            self.assertEqual(Machine.from_row(r), m)

    def test_update_machine_bad_api_key(self):
        mu = MachineUpdate(
            is_in_use=True,
            last_started_at=datetime.datetime.now(),
        )

        response: Response = client.put(
            "/machine",
            params={"floor": 14, "pos": 0},
            data=mu.json(),
            headers={"x-api-key": "bad-api-key"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_machine_good_api_key(self):
        now = datetime.datetime.now()
        mu = MachineUpdate(
            is_in_use=True,
            last_started_at=now,
        )

        response: Response = client.put(
            "/machine",
            params={"floor": 14, "pos": 0},
            data=mu.json(),
            headers={"x-api-key": "good-api-key"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check the returned entity
        m = Machine(**response.json())
        self.assertTrue(m.is_in_use)
        self.assertEqual(m.last_started_at, now)

        # and check that the database entry actually changed
        with engine.connect() as db:
            q = machine.select().where(machine.c.floor == 14).where(machine.c.pos == 0)
            r = db.execute(q).fetchone()
            self.assertIsNotNone(r)
            m = Machine.from_row(r)
            self.assertTrue(m.is_in_use)
            self.assertEqual(m.last_started_at, now)

    def test_put_machine_to_use(self):
        response = client.put(
            "/machine",
            params={"floor": self.mock_washer.floor, "pos": self.mock_washer.pos},
            data=MachineUpdate(is_in_use=True).json(),
            headers={"x-api-key": "good-api-key"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check that a record was created
        with engine.connect() as db:
            q = record.select()
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
            self.assertAlmostEqual(
                datetime.datetime.now().timestamp(),
                BaseRecord.from_row(res).time.timestamp(),
                delta=0.1,
            )

        # check that record api works
        response: Response = client.get(
            "/record",
            params={"floor": self.mock_washer.floor, "pos": self.mock_washer.pos},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rec = Record(**response.json()[0])
        self.assertEqual(rec.machine_id, self.mock_washer.id)
        self.assertEqual(rec.floor, self.mock_washer.floor)
        self.assertEqual(rec.pos, self.mock_washer.pos)
        self.assertEqual(rec.type, self.mock_washer.type)
        self.assertAlmostEqual(
            rec.time.timestamp(), datetime.datetime.now().timestamp(), delta=0.1
        )
