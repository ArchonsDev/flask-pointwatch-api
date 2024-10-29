from .base import APIError

class ResourceAlreadyExistsError(APIError):
    def __init__(self, message="Resource already exists.", status_code=409):
        super().__init__(message, status_code)

class UserAlreadyExistsError(ResourceAlreadyExistsError):
    def __init__(self, message="User already exists."):
        super().__init__(message)

class TermAlreadyExistsError(ResourceAlreadyExistsError):
    def __init__(self, message="Term already exists."):
        super().__init__(message)

class DepartmentAlreadyExistsError(ResourceAlreadyExistsError):
    def __init__(self, message="Department already exists."):
        super().__init__(message)
