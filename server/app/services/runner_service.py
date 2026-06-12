from datetime import UTC, datetime
from pydantic import ValidationError

from app.models.runner import RunnerLocation
from app.repositories.runner_repository import RunnerRepository


class RunnerService:
    def __init__(self, repository: RunnerRepository) -> None:
        self._repository = repository

    async def handle_gateway_payload(self, payload: str) -> RunnerLocation | None:
        location = self._parse_forward_payload(payload)
        if location is None:
            return None

        await self._repository.save_location(location)
        return location

    async def get_runner_location(self, runner_id: str) -> RunnerLocation | None:
        return await self._repository.get_location(runner_id)

    async def list_runner_locations(self) -> list[RunnerLocation]:
        return await self._repository.list_locations()

    def _parse_forward_payload(self, payload: str) -> RunnerLocation | None:
        fields = [field.strip() for field in payload.strip().split(",")]
        if len(fields) != 11 or fields[0] != "FORWARD":
            return None

        try:
            return RunnerLocation(
                runner_id=fields[3],
                latitude=float(fields[4]),
                longitude=float(fields[5]),
                pace=float(fields[6]),
                battery=int(fields[7]),
                received_at=datetime.now(UTC).isoformat(),
            )
        except (ValueError, ValidationError):
            return None
