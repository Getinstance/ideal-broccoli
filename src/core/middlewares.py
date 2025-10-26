import base64
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status

security = HTTPBasic()


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/metrics"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Basic "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                    content={"detail": "Authentication required"},
                )

            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)

            if username == "user" and password == "password":
                response = await call_next(request)
                return response
            else:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                    content={"detail": "Authentication required"},
                )

        response = await call_next(request)
        return response
