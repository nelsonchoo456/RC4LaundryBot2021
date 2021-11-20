from fastapi import FastAPI

from api import routers
from api.db import db, models

# initialize database table(s), may want to move elsewhere
# to a proper init func
models.metadata_obj.create_all(db.engine)
app = FastAPI()

app.include_router(routers.machine)
