from app.models.runner import RunnerLocation
from app.repositories.runner_repository import RunnerRepository
from typing import Set


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.sets: dict[str, set[str]] = {}

    async def set(self, key: str, value: str) -> None:
        self.values[key] = value

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def sadd(self, key: str, *values: str) -> None:
        self.sets.setdefault(key, set()).update(values)

    async def smembers(self, key: str) -> Set[str]:
        return self.sets.get(key, set())


async def test_repository_saves_and_lists_runner_locations() -> None:
    redis = FakeRedis()
    repository = RunnerRepository(redis)
    location = RunnerLocation(
        runner_id="7",
        latitude=36.10321,
        longitude=129.38712,
        pace=5.42,
        battery=78,
        received_at="2026-06-13T00:00:00+00:00",
    )

    await repository.save_location(location)

    assert await repository.get_location("7") == location
    assert await repository.list_locations() == [location]
