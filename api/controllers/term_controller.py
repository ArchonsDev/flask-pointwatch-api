from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import BaseController
from ..services import jwt_service, user_service, term_service, auth_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, MissingRequiredPropertyError, TermNotFoundError, AuthenticationError

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
        self.route('/<int:term_id>', methods=['GET'])(self.handle_term)
        self.route('/<int:term_id>/swtds', methods=['GET'])(self.process_terms)

    @jwt_required()
    def index(self):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            terms = self.term_service.get_all_terms()
            terms = list(filter(lambda term: term.is_deleted == False, terms))

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
    
    @jwt_required
    def handle_term(self, term_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        term = self.term_service.get_term(term_id)

        if not term or (term and term.is_deleted):
            raise TermNotFoundError()

        if request.method == 'GET':            
            return self.build_response(term.to_dict(), 200)

    @jwt_required()
    def process_terms(self, term_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        term = self.term_service.get_term(term_id)

        if not term or (term and term.is_deleted):
            raise TermNotFoundError()
        
        if request.method == 'GET':
            params = request.args
            author_id = int(params.get('author_id', 0))
            swtd_forms = term.swtd_forms

            if author_id:
                if author_id != requester.id and not self.auth_service.has_permissions(requester, 'staff'):
                    raise InsufficientPermissionsError("Must be at least staff to retrieve term SWTDs without specifying the author.")
                
                swtd_forms = list(filter(lambda swtd_form: swtd_form.author_id == author_id, swtd_forms))
            
            swtd_forms = list(filter(lambda swtd_form: swtd_form.date >= term.start_date and swtd_form.date <= term.end_date, term.swtd_forms))
            swtd_forms = list(filter(lambda form: form.is_deleted == False, swtd_forms))
            return self.build_response([swtd_form.to_dict() for swtd_form in swtd_forms], 200)

def setup(app):
    app.register_blueprint(TermController('term', __name__, url_prefix='/terms'))
