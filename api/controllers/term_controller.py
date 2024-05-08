from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import BaseController
from ..services import jwt_service, user_service, term_service, auth_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat

class TermController(Blueprint, BaseController):
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.term_service = term_service
        self.auth_service = auth_service

        self.map_routes()

    def map_routes(self):
        self.route('/', methods=['GET', 'POST'])(self.index)

    @jwt_required()
    def index(self):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if request.method == 'GET':
            terms = self.term_service.get_all_terms()

            return self.build_response({"terms": [term.to_dict() for term in terms]}, 200)
        if request.method == 'POST':
            data = request.json
            required_fields = [
                'name',
                'start_date',
                'end_date'
            ]

            self.check_fields(data, required_fields)

            if not self.auth_service.has_permissions(requester, minimum_auth='admin'):
                raise InsufficientPermissionsError("Cannot create Term,")
            
            try:
                date_fmt = '%m-%d-%Y'
                start_date = datetime.strptime(data.get('start_date'), date_fmt)
                end_date = datetime.strptime(data.get('end_date'), date_fmt)
            except Exception:
                raise InvalidDateTimeFormat()
            
            term = self.term_service.create_term(
                data.get('name'),
                start_date,
                end_date
            )

            return self.build_response(term.to_dict(), 200)

def setup(app):
    app.register_blueprint(TermController('term', __name__, url_prefix='/terms'))
