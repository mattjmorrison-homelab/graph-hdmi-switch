import json
from pathlib import Path
from wsgiref.types import StartResponse, WSGIEnvironment

_LOGO_PATH = Path(__file__).parent / "logo.png"


def app(environ: WSGIEnvironment, start_response: StartResponse) -> list[bytes]:
    if environ.get("PATH_INFO") == "/logo":
        body = _LOGO_PATH.read_bytes()
        headers = [("Content-Type", "image/png")]
    else:
        body = json.dumps({"Hello - 3": "World - 3"}).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
        ]

    start_response("200 OK", headers)
    return [body]
