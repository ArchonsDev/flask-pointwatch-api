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

class TermNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass
