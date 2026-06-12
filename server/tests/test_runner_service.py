from app.services.runner_service import RunnerService


class FakeRepository:
    def __init__(self) -> None:
        self.saved = None

    async def save_location(self, location):
        self.saved = location

    async def get_location(self, runner_id: str):
        return self.saved if self.saved and self.saved.runner_id == runner_id else None

    async def list_locations(self):
        return [self.saved] if self.saved else []


async def test_handle_gateway_payload_saves_forward_location() -> None:
    repository = FakeRepository()
    service = RunnerService(repository)

    location = await service.handle_gateway_payload(
        "FORWARD,1,2,7,36.10321,129.38712,5.42,78,10,-91,7.2"
    )

    assert location is not None
    assert location.runner_id == "7"
    assert location.latitude == 36.10321
    assert location.longitude == 129.38712
    assert repository.saved == location


async def test_handle_gateway_payload_ignores_invalid_payload() -> None:
    repository = FakeRepository()
    service = RunnerService(repository)

    location = await service.handle_gateway_payload("DONE,1,2,3")

    assert location is None
    assert repository.saved is None
