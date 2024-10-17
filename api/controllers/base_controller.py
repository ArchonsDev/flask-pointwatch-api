from typing import Any

from flask import jsonify, Response

from ..exceptions import *

class BaseController:
    def build_response(self, response: Any, code: int) -> Response:
        if code >= 400 and code <= 599:
            return jsonify({"error": response}), code
        
        return jsonify(response), code

    def check_fields(self, data: dict[str, Any], required_fields: list[str]):
        for field in required_fields:
            if field not in data:
                raise MissingRequiredPropertyError(field)
