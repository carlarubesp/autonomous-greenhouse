from typing import Any

from greenhouse_common.knowledge import KnowledgeClient


class FakeResponse:
    def __init__(self, body: Any = None):
        self._body = body

    def json(self) -> Any:
        return self._body


class FakeSession:
    """Records requests and returns canned bodies."""

    def __init__(self, body: Any = None):
        self.body = body
        self.calls: list[tuple[str, str, Any]] = []

    def get(self, url: str) -> FakeResponse:
        self.calls.append(("GET", url, None))
        return FakeResponse(self.body)

    def post(self, url: str, json: Any = None) -> FakeResponse:
        self.calls.append(("POST", url, json))
        return FakeResponse(self.body)


def make_client(body: Any = None) -> tuple[KnowledgeClient, FakeSession]:
    session = FakeSession(body)
    return KnowledgeClient("http://knowledge:5000/", session=session), session  # type: ignore[arg-type]


def test_add_reading_posts_to_sensors() -> None:
    client, session = make_client()

    client.add_reading({"clock": 1})

    assert session.calls == [("POST", "http://knowledge:5000/sensors", {"clock": 1})]


def test_get_short_term_returns_body() -> None:
    client, session = make_client([{"clock": 1}])

    assert client.get_short_term() == [{"clock": 1}]
    assert session.calls == [("GET", "http://knowledge:5000/short-term", None)]


def test_reset_short_term() -> None:
    client, session = make_client()

    client.reset_short_term()

    assert session.calls == [("POST", "http://knowledge:5000/short-term/reset", None)]


def test_actuators_round_trip() -> None:
    client, session = make_client({"fan": True})

    assert client.get_actuators() == {"fan": True}
    assert client.update_actuators({"fan": True}) == {"fan": True}
    assert session.calls[1] == ("POST", "http://knowledge:5000/actuators", {"fan": True})
