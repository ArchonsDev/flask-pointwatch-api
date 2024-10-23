from .base import APIError

class ValidationError(APIError):
    def __init__(self, message="Validation failed.", status_code=400):
        super().__init__(message, status_code)

class MissingRequiredParameterError(ValidationError):
    def __init__(self, field_name):
        super().__init__(message=f"Missing required field: {field_name}")

class InvalidParameterError(ValidationError):
    def __init__(self, field_name):
        super().__init__(message=f"Invalid paramter: {field_name}")

class InsufficientPointsError(ValidationError):
    def __init__(self, required_points):
        super().__init__(message=f"At least {required_points} is required.")

class InvalidDateTimeFormat(ValidationError):
    def __init__(self, message="Date/Time format is invalid."):
        super().__init__(message)
