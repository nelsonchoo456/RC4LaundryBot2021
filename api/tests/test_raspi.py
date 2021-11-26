from unittest import TestCase

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from shortuuid import uuid

from api.db.db import engine
from api.db.models import api_key, metadata_obj, raspi
from api.main import app
from api.raspi import Raspi, RaspiUpdate
from api.tests.mocks import get_api_key, get_mock_pi

client = TestClient(app)


class TestRaspi(TestCase):
    pi_one = get_mock_pi()
    pi_two = get_mock_pi()
    good_api_key = get_api_key()
    bad_api_key = get_api_key()

    @classmethod
    def tearDownClass(cls):
        metadata_obj.drop_all(engine)

    def setUp(self):
        metadata_obj.drop_all(engine)
        metadata_obj.create_all(engine)

        # insert some pis
        with engine.connect() as db:
            db.execute(raspi.insert(), [self.pi_one.dict(), self.pi_two.dict()])
            db.execute(api_key.insert().values(api_key=self.good_api_key))

    def test_get_raspi_bad_api_key(self):
        response = client.get("/raspi", headers={"x-api-key": self.bad_api_key})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_raspi(self):
        response = client.get("/raspi", headers={"x-api-key": self.good_api_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertCountEqual(
            response.json(),
            [jsonable_encoder(self.pi_one), jsonable_encoder(self.pi_two)],
        )

        # now with query param
        response = client.get(
            "/raspi",
            params={"floor": self.pi_one.floor},
            headers={"x-api-key": self.good_api_key},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.json(), [jsonable_encoder(self.pi_one)])

    def test_update_raspi(self):
        # pretend to upate the ip address for pi one
        ru = RaspiUpdate(ip_addr=uuid())
        response = client.put(
            "/raspi",
            headers={"x-api-key": self.good_api_key},
            data=ru.json(),
            params={"floor": self.pi_one.floor},
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.json()["ip_addr"], ru.ip_addr)

        # check that the pi was actually updated
        with engine.connect() as db:
            q = raspi.select().where(raspi.c.floor == self.pi_one.floor)
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
            self.assertEqual(res.ip_addr, ru.ip_addr)

        # try and update a non-existent raspberry pi
        response = client.put(
            "/raspi",
            headers={"x-api-key": self.good_api_key},
            data=ru.json(),
            params={"floor": self.pi_two.floor + 420},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_raspi(self):
        rp = Raspi(floor=self.pi_two.floor + 1, ip_addr=uuid())
        response = client.post(
            "raspi", headers={"x-api-key": self.good_api_key}, data=rp.json()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that the pi was actually created
        with engine.connect() as db:
            q = raspi.select().where(raspi.c.floor == rp.floor)
            res = db.execute(q).fetchone()
            self.assertIsNotNone(res)
