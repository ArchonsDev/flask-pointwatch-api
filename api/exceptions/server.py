from .base import APIError

class ServerError(APIError):
    def __init__(self, message="Internal server error.", status_code=500):
        super().__init__(message, status_code)
