import json
from wsgiref.types import StartResponse, WSGIEnvironment


def app(environ: WSGIEnvironment, start_response: StartResponse) -> list[bytes]:
    body = json.dumps({"Hello": "World"}).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ]
    start_response("200 OK", headers)
    return [body]
