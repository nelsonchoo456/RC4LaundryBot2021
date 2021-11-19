from db import db, models
from fastapi import FastAPI
import routers

# initialize database table(s), may want to move elsewhere
# to a proper init func
models.metadata_obj.create_all(db.engine)
app = FastAPI()

app.include_router(routers.machine)
