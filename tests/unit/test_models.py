from readeck_cli.models.auth import TokenInfo
from readeck_cli.models.bookmark import Bookmark, BookmarkUpdated
from readeck_cli.models.collection import Collection
from readeck_cli.models.highlight import Highlight
from readeck_cli.models.label import Label
from readeck_cli.models.profile import UserProfile


def test_token_info_parses() -> None:
    data = {
        "id": "t1",
        "token": "abc123",
        "application": "readeck-cli",
        "created": "2026-01-01T00:00:00Z",
    }
    token = TokenInfo.model_validate(data)
    assert token.id == "t1"
    assert token.token == "abc123"


def test_bookmark_parses_minimal() -> None:
    data = {
        "id": "b1",
        "href": "/api/bookmarks/b1",
        "url": "https://example.com",
        "title": "Example",
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }
    bm = Bookmark.model_validate(data)
    assert bm.id == "b1"
    assert bm.url == "https://example.com"
    assert bm.labels == []
    assert bm.is_archived is False


def test_bookmark_parses_full() -> None:
    data = {
        "id": "b2",
        "href": "/api/bookmarks/b2",
        "url": "https://blog.example.com/post",
        "title": "A Post",
        "state": 0,
        "loaded": True,
        "type": "article",
        "document_type": "article",
        "description": "Nice post",
        "authors": ["Alice"],
        "lang": "en",
        "labels": ["tech", "python"],
        "is_archived": True,
        "is_marked": False,
        "is_deleted": False,
        "read_progress": 10,
        "reading_time": 5,
        "word_count": 1200,
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-02T00:00:00Z",
        "site_name": "Example Blog",
        "site": "blog.example.com",
        "resources": {
            "image": {"src": "https://example.com/img.png", "width": 800, "height": 480}
        },
    }
    bm = Bookmark.model_validate(data)
    assert bm.labels == ["tech", "python"]
    assert bm.is_archived is True
    assert bm.reading_time == 5
    assert bm.loaded is True
    assert bm.resources is not None
    assert bm.resources.image is not None
    assert bm.resources.image.width == 800


def test_bookmark_updated_parses() -> None:
    data = {
        "id": "b1",
        "href": "/api/bookmarks/b1",
        "title": "New Title",
        "updated": "2026-01-02T00:00:00Z",
    }
    bm = BookmarkUpdated.model_validate(data)
    assert bm.id == "b1"
    assert bm.title == "New Title"


def test_label_parses() -> None:
    data = {"name": "python", "count": 3}
    label = Label.model_validate(data)
    assert label.name == "python"
    assert label.count == 3


def test_collection_parses() -> None:
    data = {
        "id": "c1",
        "title": "Reading List",
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }
    col = Collection.model_validate(data)
    assert col.title == "Reading List"


def test_highlight_parses() -> None:
    data = {
        "id": "h1",
        "bookmark_id": "b1",
        "text": "Important quote",
        "created": "2026-01-01T00:00:00Z",
    }
    h = Highlight.model_validate(data)
    assert h.text == "Important quote"


def test_user_profile_parses() -> None:
    data = {"id": "u1", "username": "stephane", "email": "stephane@example.com"}
    profile = UserProfile.model_validate(data)
    assert profile.username == "stephane"
