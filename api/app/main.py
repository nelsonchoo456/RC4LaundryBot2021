from app import routers
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

app.include_router(routers.machine)
app.include_router(routers.raspi)

handler = Mangum(app)
