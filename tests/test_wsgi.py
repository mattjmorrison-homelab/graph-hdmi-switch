import io
import json
import os
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock, patch
from wsgiref.types import StartResponse, WSGIEnvironment

from homelab_hdmi_switch.switch import HdmiInputPort, SwitchCommunicationError
from homelab_hdmi_switch.wsgi import app


class _CapturedResponse:
    """Records the status and headers passed to a start_response call."""

    def __init__(self) -> None:
        self.status = ""
        self.headers: list[tuple[str, str]] = []


def _capturing_start_response() -> tuple[StartResponse, _CapturedResponse]:
    """Build a start_response callable that records its status and headers."""
    captured = _CapturedResponse()

    def start_response(
        status: str,
        headers: list[tuple[str, str]],
        exc_info: object = None,
    ) -> Callable[[bytes], object]:
        captured.status = status
        captured.headers = headers
        return lambda data: None

    return start_response, captured


def _graphql_environ(request_body: bytes) -> WSGIEnvironment:
    return {
        "PATH_INFO": "/graphql",
        "REQUEST_METHOD": "POST",
        "CONTENT_LENGTH": str(len(request_body)),
        "wsgi.input": io.BytesIO(request_body),
    }


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


def test_graphql_route_returns_inputs_query_result() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps(
        {"query": "{ inputs { value label icon hoverText isActive } }"}
    ).encode("utf-8")
    with patch(
        "homelab_hdmi_switch.schema.switch.get_current_input",
        return_value=HdmiInputPort.PS4,
    ):
        body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    parsed = json.loads(b"".join(body))
    inputs = parsed["data"]["inputs"]
    assert [entry["value"] for entry in inputs] == [
        "APPLE_TV",
        "PC",
        "SWITCH",
        "PS3",
        "PS4",
    ]
    active = [entry for entry in inputs if entry["isActive"]]
    assert active == [
        {
            "value": "PS4",
            "label": "PS4",
            "icon": "gamepad-2",
            "hoverText": "PlayStation 4",
            "isActive": True,
        }
    ]
    assert ("Content-Type", "application/json") in captured.headers


def test_graphql_mutation_sets_input_and_returns_new_state() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps(
        {"query": "mutation { setInput(input: APPLE_TV) }"}
    ).encode("utf-8")
    with patch(
        "homelab_hdmi_switch.schema.switch.set_input",
        return_value=HdmiInputPort.APPLE_TV,
    ) as mock_set_input:
        body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    assert json.loads(b"".join(body)) == {"data": {"setInput": "APPLE_TV"}}
    mock_set_input.assert_called_once_with(HdmiInputPort.APPLE_TV)


def test_graphql_route_surfaces_switch_communication_error() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps({"query": "{ inputs { value } }"}).encode("utf-8")
    with patch(
        "homelab_hdmi_switch.schema.switch.get_current_input",
        side_effect=SwitchCommunicationError("device unreachable"),
    ):
        body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    parsed = json.loads(b"".join(body))
    assert parsed["data"] is None
    assert any("device unreachable" in error["message"] for error in parsed["errors"])


def test_graphql_route_passes_variables_to_execute_sync() -> None:
    start_response, _ = _capturing_start_response()

    request_body = json.dumps(
        {"query": "{ hello }", "variables": {"foo": "bar"}}
    ).encode("utf-8")

    with patch("homelab_hdmi_switch.wsgi.schema.execute_sync") as mock_execute_sync:
        mock_execute_sync.return_value = Mock(data={"hello": "x"}, errors=None)
        app(_graphql_environ(request_body), start_response)

    assert mock_execute_sync.call_args.kwargs["variable_values"] == {"foo": "bar"}


def test_graphql_route_returns_errors_for_invalid_query() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps({"query": "{ hello "}).encode("utf-8")
    body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    parsed = json.loads(b"".join(body))
    assert "errors" in parsed
    assert isinstance(parsed["errors"], list)
    assert len(parsed["errors"]) > 0
    for entry in parsed["errors"]:
        assert isinstance(entry, dict)
        assert isinstance(entry["message"], str)


def test_graphql_service_sdl_query_returns_federation_sdl() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps({"query": "{ _service { sdl } }"}).encode("utf-8")
    body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    parsed = json.loads(b"".join(body))
    sdl = parsed["data"]["_service"]["sdl"]
    assert isinstance(sdl, str) and len(sdl) > 0


def test_graphql_get_request_falls_through_to_default_response() -> None:
    start_response, captured = _capturing_start_response()

    environ = {"PATH_INFO": "/graphql", "REQUEST_METHOD": "GET"}
    body = app(environ, start_response)

    assert captured.status == "200 OK"
    assert b"".join(body) == json.dumps({"Hello - 3": "World - 3"}).encode("utf-8")
    assert ("Content-Type", "application/json") in captured.headers


def test_graphql_route_returns_errors_for_invalid_json_body() -> None:
    start_response, captured = _capturing_start_response()

    request_body = b"not valid json {{{"
    body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    assert json.loads(b"".join(body)) == {"errors": [{"message": "invalid JSON body"}]}


def test_graphql_route_returns_errors_for_nonexistent_field() -> None:
    start_response, captured = _capturing_start_response()

    request_body = json.dumps({"query": "{ nonexistentField }"}).encode("utf-8")
    body = app(_graphql_environ(request_body), start_response)

    assert captured.status == "200 OK"
    parsed = json.loads(b"".join(body))
    assert "errors" in parsed
    assert isinstance(parsed["errors"], list)
    assert len(parsed["errors"]) > 0
    for entry in parsed["errors"]:
        assert isinstance(entry, dict)
        assert isinstance(entry["message"], str)


def test_version_route_returns_commit_sha_from_env() -> None:
    start_response, captured = _capturing_start_response()

    environ = {"PATH_INFO": "/version", "REQUEST_METHOD": "GET"}
    with patch.dict(os.environ, {"COMMIT_SHA": "abc1234"}):
        body = app(environ, start_response)

    assert captured.status == "200 OK"
    assert json.loads(b"".join(body)) == {"commit_sha": "abc1234"}
    assert ("Content-Type", "application/json") in captured.headers
