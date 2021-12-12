from typing import List, Optional

from app.auth import validate_api_key
from app.raspi import (
    IRaspiService,
    RaspiFilter,
    RaspiIn,
    RaspiOut,
    RaspiUpdate,
    _field_floor,
    _field_ip_addr,
)
from app.redis.raspi import get_raspi_service
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(prefix="/raspi", dependencies=[Depends(validate_api_key)])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Creates a new raspi. Fails if a raspi at the same floor already exists.",
)
async def create_raspi(rpi: RaspiIn, rs: IRaspiService = Depends(get_raspi_service)):
    rs.create(rpi)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[RaspiOut],
    description="Get a list of raspis.",
)
async def get_raspis(
    floor: Optional[int] = Query(None, description=_field_floor.description),
    ip_addr: Optional[str] = Query(None, description=_field_ip_addr.description),
    rs: IRaspiService = Depends(get_raspi_service),
):
    return rs.find(RaspiFilter(floor=floor, ip_addr=ip_addr))


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=RaspiOut,
    description="Performs partial update of a raspi.",
)
async def update_raspi(
    ru: RaspiUpdate,
    floor: int = Query(..., description=_field_floor.description),
    rs: IRaspiService = Depends(get_raspi_service),
):
    return rs.update(floor, ru)


@router.put(
    "",
    status_code=status.HTTP_200_OK,
    description="Performs upsert for a raspi.",
)
async def upsert_raspi(
    rpi: RaspiIn,
    rs: IRaspiService = Depends(get_raspi_service),
):
    rs.upsert(rpi)
