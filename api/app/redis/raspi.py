from app.raspi import RaspiFilter, RaspiIn, RaspiOut, RaspiUpdate
from fastapi import Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.logger import logger
from redis import Redis
from redis.commands.json import JSON as RedisJSON
from redis.commands.search import Search as RediSearch
from redis.commands.search.document import Document
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.exceptions import ResponseError

from . import get_redis


class RaspiService:
    """Service class implementing the IRaspiService interface,
    with Redis as the datastore."""

    root_path: str = "."

    def __init__(self, redis: Redis):
        self.redis = redis
        self.rj: RedisJSON = redis.json()
        self.rs: RediSearch = redis.ft(index_name="raspiIdx")

        # create the index
        try:
            self.rs.create_index(
                [
                    NumericField("$.floor", sortable=True, as_name="floor"),
                    TextField("$.ip_addr", sortable=True, as_name="ip_addr"),
                ],
                definition=IndexDefinition(
                    index_type=IndexType.JSON, prefix=["raspi:"]
                ),
            )
        except ResponseError as e:
            logger.info(e)

    def create(self, rpi: RaspiIn):
        """Creates a raspi. Fails if a raspi at the same floor
        already exists."""
        res = self.rj.set(
            rpi.create_key(),
            self.root_path,
            jsonable_encoder(rpi.to_raspi_out()),
            nx=True,
        )
        if res is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Raspi at floor {rpi.floor} already exists.",
            )

    def upsert(self, rpi: RaspiIn):
        """Performs upsert for a raspi."""

        self.rj.set(
            rpi.create_key(), self.root_path, jsonable_encoder(rpi.to_raspi_out())
        )

    def find(self, rf: RaspiFilter):
        """Queries Redis for raspis, based on the filter provided."""
        res = self.rs.search(self.build_query(rf))
        return [self.from_document(doc) for doc in res.docs]

    def update(self, floor: int, ru: RaspiUpdate):
        """Performs partial update of a raspi."""
        key = RaspiIn._create_key(floor)
        res = self.rj.get(key)
        if res is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Raspi at floor {floor} was not found.",
            )
        old = RaspiIn(**res)
        new = old.copy(update=ru.dict(exclude_unset=True, exclude_none=True))
        self.rj.set(key, self.root_path, jsonable_encoder(new))
        return new

    def delete(self, floor: int):
        """Deletes a raspi."""
        raise NotImplementedError()

    @staticmethod
    def build_query(rf: RaspiFilter):
        def floor(v: int):
            return f"@floor:[{v} {v}]"

        def ip_addr(v: str):
            return f"@ip_addr:{v}"

        q_mapping = {"floor": floor, "ip_addr": ip_addr}
        rf_dict = rf.dict(exclude_none=True, exclude_unset=True)

        if not rf_dict:
            return "*"
        return " ".join([q_mapping[k](v) for k, v in rf_dict.items()])

    @staticmethod
    def from_document(doc: Document) -> RaspiOut:
        return RaspiOut.from_json(doc.__dict__["json"])


def get_raspi_service(redis: Redis = Depends(get_redis)):
    return RaspiService(redis)
