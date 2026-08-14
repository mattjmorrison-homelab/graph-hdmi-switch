import json
from collections.abc import Callable

from homelab_hdmi_switch.wsgi import app


def test_app_returns_hello_world_json() -> None:
    captured_status = ""
    captured_headers: list[tuple[str, str]] = []

    def start_response(
        status: str,
        headers: list[tuple[str, str]],
        exc_info: object = None,
    ) -> Callable[[bytes], object]:
        nonlocal captured_status, captured_headers
        captured_status = status
        captured_headers = headers
        return lambda data: None

    body = app({}, start_response)

    assert captured_status == "200 OK"
    assert b"".join(body) == json.dumps({"Hello - 2": "World - 2"}).encode("utf-8")
    assert ("Content-Type", "application/json") in captured_headers
