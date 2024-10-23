from .base import APIError

class AuthorizationError(APIError):
    def __ini__(self, message="Unauthorized action.", status_code=403):
        super().__init__(message, status_code)
