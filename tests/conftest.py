# tests/conftest.py
import os

import pytest
from readeck_cli.client.http import ReadeckClient
from readeck_cli.config import Config


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "e2e: end-to-end tests requiring READECK_URL + READECK_TOKEN"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.environ.get("READECK_E2E") != "1":
        skip = pytest.mark.skip(reason="Set READECK_E2E=1 to run e2e tests")
        for item in items:
            if item.get_closest_marker("e2e"):
                item.add_marker(skip)


@pytest.fixture
def e2e_config() -> Config:
    url = os.environ.get("READECK_URL")
    token = os.environ.get("READECK_TOKEN")
    if not url or not token:
        pytest.skip("READECK_URL and READECK_TOKEN required")
    return Config(url=url, token=token)


@pytest.fixture
async def e2e_client(e2e_config: Config) -> ReadeckClient:
    async with ReadeckClient(e2e_config.url, e2e_config.token) as client:
        yield client  # type: ignore[misc]
