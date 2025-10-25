import secrets
from typing import Callable
from urllib.parse import parse_qs
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Request, HTTPException, status
from prometheus_client.exposition import _bake_output
from prometheus_client.registry import CollectorRegistry, REGISTRY

security = HTTPBasic()


async def verify_username(request: Request) -> HTTPBasicCredentials:

    credentials = await security(request)

    correct_username = secrets.compare_digest(credentials.username, "user")
    correct_password = secrets.compare_digest(credentials.password, "password")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def make_asgi_sec_app(
    registry: CollectorRegistry = REGISTRY, disable_compression: bool = False
) -> Callable:
    """Create a ASGI app which serves the metrics from a registry."""

    async def prometheus_app(scope, receive, send):
        assert scope.get("type") == "http"

        # Verify username and password
        request = Request(scope, receive)
        await verify_username(request)

        # Prepare parameters
        params = parse_qs(scope.get("query_string", b"").decode("utf8"))
        accept_header = ",".join(
            [
                value.decode("utf8")
                for (name, value) in scope.get("headers")
                if name.decode("utf8").lower() == "accept"
            ]
        )
        accept_encoding_header = ",".join(
            [
                value.decode("utf8")
                for (name, value) in scope.get("headers")
                if name.decode("utf8").lower() == "accept-encoding"
            ]
        )
        # Bake output
        status, headers, output = _bake_output(
            registry, accept_header, accept_encoding_header, params, disable_compression
        )
        formatted_headers = []
        for header in headers:
            formatted_headers.append(tuple(x.encode("utf8") for x in header))
        # Return output
        payload = await receive()
        if payload.get("type") == "http.request":
            await send(
                {
                    "type": "http.response.start",
                    "status": int(status.split(" ")[0]),
                    "headers": formatted_headers,
                }
            )
            await send({"type": "http.response.body", "body": output})

    return prometheus_app
