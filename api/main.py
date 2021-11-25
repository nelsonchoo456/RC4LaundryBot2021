"""Entry point for starting the server"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from api import routers
from api.db import db, models, seed

load_dotenv()


# initialize database table(s), may want to move elsewhere
# to a proper init func
models.metadata_obj.create_all(db.engine)
if os.environ.get("RUN_ENV") == "dev":
    with db.engine.connect() as c:
        seed.seed_machines(c)

app = FastAPI()

app.include_router(routers.machine)
app.include_router(routers.usage)
