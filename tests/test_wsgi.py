import json
from collections.abc import Callable
from pathlib import Path

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
    assert b"".join(body) == json.dumps({"Hello - 3": "World - 3"}).encode("utf-8")
    assert ("Content-Type", "application/json") in captured_headers


def test_logo_route_returns_png_image() -> None:
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

    environ = {"PATH_INFO": "/logo", "REQUEST_METHOD": "GET"}
    body = app(environ, start_response)

    logo_path = (
        Path(__file__).parent.parent / "src" / "homelab_hdmi_switch" / "logo.png"
    )
    assert captured_status == "200 OK"
    assert b"".join(body) == logo_path.read_bytes()
    assert ("Content-Type", "image/png") in captured_headers
