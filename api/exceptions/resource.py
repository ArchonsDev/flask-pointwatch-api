from .base import APIError

class ResourceNotFoundError(APIError):
    def __init__(self, message="Resource not found.", status_code=404):
        super().__init__(message, status_code)

class UserNotFoundError(ResourceNotFoundError):
    def __init__(self, message="User not found."):
        super().__init__(message)

class TermNotFoundError(ResourceNotFoundError):
    def __init__(self, message="Term not found."):
        super().__init__(message)

class SWTDFormNotFoundError(ResourceNotFoundError):
    def __init__(self, message="SWTDForm not found."):
        super().__init__(message)

class SWTDCommentNotFoundError(ResourceNotFoundError):
    def __init__(self, message="SWTDComment not found."):
        super().__init__(message)

class ProofNotFoundError(ResourceNotFoundError):
    def __init__(self, message="Proof not found."):
        super().__init__(message)

class NotificationNotFoundError(ResourceNotFoundError):
    def __init__(self, message="Notification not found."):
        super().__init__(message)

class DepartmentNotFoundError(ResourceNotFoundError):
    def __init__(self, message="Department not found."):
        super().__init__(message)

class ClearingNotFoundError(ResourceNotFoundError):
    def __init__(self, message="Clearing not found."):
        super().__init__(message)
