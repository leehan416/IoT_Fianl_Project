from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.runner import RunnerLocation
from app.repositories.runner_repository import RunnerRepository
from app.services.runner_service import RunnerService

router = APIRouter(prefix="/runners", tags=["runners"])


def get_runner_service(request: Request) -> RunnerService:
    return RunnerService(RunnerRepository(request.app.state.redis))


@router.get("", response_model=list[RunnerLocation])
async def list_runners(
    runner_service: RunnerService = Depends(get_runner_service),
) -> list[RunnerLocation]:
    return await runner_service.list_runner_locations()


@router.get("/{runner_id}", response_model=RunnerLocation)
async def get_runner(
    runner_id: str,
    runner_service: RunnerService = Depends(get_runner_service),
) -> RunnerLocation:
    location = await runner_service.get_runner_location(runner_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Runner location not found",
        )
    return location
