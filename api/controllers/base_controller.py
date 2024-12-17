from typing import Any

from flask import jsonify, Response
from marshmallow import Schema, ValidationError

from ..exceptions.validation import MissingRequiredParameterError

class BaseController:
    def build_response(self, response: Any, code: int) -> Response:
        if code >= 400 and code <= 599:
            return jsonify({"error": response}), code
        
        return jsonify(response), code

    def check_fields(self, data: dict[str, Any], required_fields: list[str]):
        for field in required_fields:
            if field not in data:
                raise MissingRequiredParameterError(field)
            
    def parse_form(self, form: dict[str, Any], schema: Schema) -> Schema:
        try:
            data = schema().load(form)
            
            return data
        except ValidationError as e:
            return self.build_response(jsonify({"errors": e.messages}), 400)
