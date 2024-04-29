from .exceptions import *
from .controllers.base_controller import build_response

def handle_exception(e):
    if isinstance(e, AccountUnavailableError):
        return build_response("Account unavailable.", 403)
    elif isinstance(e, AuthenticationError):
        return build_response("Unauthorized user.", 401)
    elif isinstance(e, DuplicateValueError):
        return build_response(f"'{e.name}' already exists.", 409)
    elif isinstance(e, InvalidDateTimeFormat):
        return build_response("Request contains an invalid Date/Time format. Use 'mm-dd-yyyy HH:MM'.", 400)
    elif isinstance(e, InvalidParameterError):
        return build_response(f"Invalid parameter: '{e.param}'.", 400)
    elif isinstance(e, InsufficientPermissionsError):
        return build_response(f"Insufficient permissions. {e.args[0]}", 403)
    elif isinstance(e, MissingRequiredPropertyError):
        return build_response(f"'{e.property}' is required.", 400)
    elif isinstance(e, ResourceNotFoundError):
        return build_response("The requested resource is not available.", 404)
    elif isinstance(e, SWTDFormNotFoundError):
        return build_response("SWTD Form not found.", 404)
    elif isinstance(e, UserNotFoundError):
        return build_response("User not found.", 404)
    else:
        return build_response(f"An error occurred.", 500)
