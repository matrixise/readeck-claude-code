# tests/e2e/test_e2e.py
import pytest

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.bookmarks import BookmarkService
from readeck_cli.services.labels import LabelService
from readeck_cli.services.profile import ProfileService


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_profile_returns_username(e2e_client: ReadeckClient) -> None:
    service = ProfileService(e2e_client)
    profile = await service.get()
    assert profile.username


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_list_bookmarks_returns_list(e2e_client: ReadeckClient) -> None:
    service = BookmarkService(e2e_client)
    bookmarks, total = await service.list(limit=5)
    assert isinstance(bookmarks, list)
    assert total >= 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_list_labels_returns_list(e2e_client: ReadeckClient) -> None:
    service = LabelService(e2e_client)
    labels = await service.list()
    assert isinstance(labels, list)
