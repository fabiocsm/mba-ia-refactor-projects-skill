import hmac
from functools import wraps

from flask import current_app, request

from utils.constants import ADMIN_TOKEN_HEADER
from utils.errors import ForbiddenError, UnauthorizedError


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        if not expected:
            raise ForbiddenError("Endpoint administrativo desabilitado")
        provided = request.headers.get(ADMIN_TOKEN_HEADER, "")
        if not hmac.compare_digest(provided, expected):
            raise UnauthorizedError("Token administrativo inválido ou ausente")
        return view(*args, **kwargs)

    return wrapper
