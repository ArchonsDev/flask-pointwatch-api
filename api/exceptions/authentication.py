from .base import APIError

class AuthenticationError(APIError):
    def __init__(self, message="Authentication failed.", status_code=401):
        super().__init__(message, status_code)
