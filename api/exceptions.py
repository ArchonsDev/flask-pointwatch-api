class AccountUnavailableError(Exception):
    pass

class AuthenticationError(Exception):
    pass
class DuplicateValueError(Exception):
    def __init__(self, name):
        super().__init__()
        self.name = name

class InvalidDateTimeFormat(Exception):
    pass

class InvalidParameterError(Exception):
    def __init__(self, param):
        super().__init__()
        self.param = param

class InsufficientPermissionsError(Exception):
    pass

class InsufficientSWTDPointsError(Exception):
    def __init__(self, points):
        super().__init__()
        self.points = points

class MissingRequiredPropertyError(Exception):
    def __init__(self, property):
        super().__init__()
        self.property = property

class ResourceNotFoundError(Exception):
    pass

class SWTDCommentNotFoundError(Exception):
    pass

class SWTDFormNotFoundError(Exception):
    pass

class TermClearingError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class TermNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass
