import json
from typing import Protocol, Set

from app.models.runner import RunnerLocation


class RedisLike(Protocol):
    async def set(self, key: str, value: str) -> object:
        ...

    async def get(self, key: str) -> str | bytes | None:
        ...

    async def sadd(self, key: str, *values: str) -> object:
        ...

    async def smembers(self, key: str) -> Set[str] | Set[bytes]:
        ...


class RunnerRepository:
    def __init__(self, redis_client: RedisLike) -> None:
        self._redis = redis_client

    async def save_location(self, location: RunnerLocation) -> None:
        await self._redis.set(
            self._location_key(location.runner_id),
            location.model_dump_json(),
        )
        await self._redis.sadd("runners", location.runner_id)

    async def get_location(self, runner_id: str) -> RunnerLocation | None:
        value = await self._redis.get(self._location_key(runner_id))
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        try:
            return RunnerLocation.model_validate(json.loads(value))
        except (json.JSONDecodeError, ValueError, TypeError):
            return None

    async def list_locations(self) -> list[RunnerLocation]:
        runner_ids = await self._redis.smembers("runners")
        locations: list[RunnerLocation] = []

        for runner_id in sorted(self._decode_runner_ids(runner_ids)):
            location = await self.get_location(runner_id)
            if location is not None:
                locations.append(location)

        return locations

    @staticmethod
    def _location_key(runner_id: str) -> str:
        return f"runner:{runner_id}:location"

    @staticmethod
    def _decode_runner_ids(runner_ids: Set[str] | Set[bytes]) -> list[str]:
        return [
            runner_id.decode("utf-8") if isinstance(runner_id, bytes) else runner_id
            for runner_id in runner_ids
        ]
