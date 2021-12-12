import boto3
from app.config import get_settings

settings = get_settings()
db = boto3.resource(
    "dynamodb",
    endpoint_url=settings.dynamodb_url,
    region_name=settings.dynamodb_region,
)


def get_dynamodb():
    return db
