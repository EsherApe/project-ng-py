import logging
from datetime import datetime, timedelta
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from sqlmodel import Session, select
from jose import jwt, JWTError

from backend.app.db.database import get_db
from backend.app.models.token import RefreshToken
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.security import create_access_token

logger = logging.getLogger(__name__)

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT token refresh logic
    - Checks if token is about to expire and refreshes it
    """

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Process the request and get the response
        response = await call_next(request)

        # Skip refresh for non-authenticated paths
        path = request.url.path
        if path.endswith(("/login", "/refresh", "/logout", "/docs", "/openapi.json")):
            return response

        # Extract authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return response

        # Extract the token
        token = auth_header.replace("Bearer ", "")

        try:
            # Decode JWT
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Check if token is about to expire
            exp = datetime.fromtimestamp(payload.get("exp"))
            now = datetime.now()

            # If token expires in less than 5 minutes, refresh it
            if exp - now < timedelta(minutes=5):
                # Get a database session
                db = next(get_db())

                try:
                    # Get user
                    user_id = int(payload.get("sub"))
                    user = db.get(User, user_id)

                    if user and not user.disabled:
                        # Create new access token
                        roles = user.roles.split(",") if user.roles else []
                        new_token = create_access_token(
                            subject=str(user.id),
                            username=user.username,
                            roles=roles,
                        )

                        # Set new token in response header
                        response.headers["X-New-Access-Token"] = new_token
                        response.headers["Access-Control-Expose-Headers"] = "X-New-Access-Token"
                finally:
                    db.close()

        except (JWTError, ValueError) as e:
            # Log error but don't stop request processing
            logger.error(f"Error refreshing token: {str(e)}")

        return response