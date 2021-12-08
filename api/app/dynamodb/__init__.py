import boto3
from app.config import Settings, get_settings
from fastapi import Depends


def get_dynamodb(settings: Settings = Depends(get_settings)):
    db = boto3.resource(
        "dynamodb",
        endpoint_url=settings.dynamodb_url,
        region_name=settings.dynamodb_region,
    )
    return db
