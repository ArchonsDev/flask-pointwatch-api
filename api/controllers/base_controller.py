from flask import jsonify

from ..exceptions import *

class BaseController:
    def build_response(self, response, code):
        if code >= 400 and code <= 599:
            return jsonify({"error": response}), code
        
        return jsonify(response), code

    def check_fields(self, data, required_fields):
        for field in required_fields:
            if not data.get(field):
                raise MissingRequiredPropertyError(field)
