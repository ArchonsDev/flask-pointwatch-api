from typing import Any
from datetime import datetime

from flask import Blueprint, request, Response, Flask, redirect, url_for
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, term_service, auth_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, MissingRequiredPropertyError, TermNotFoundError, AuthenticationError

class TermController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.term_service = term_service
        self.auth_service = auth_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/', methods=['GET', 'POST'])(self.index)
        self.route('/<int:term_id>', methods=['GET', 'PUT', 'DELETE'])(self.handle_term)
        self.route('/<int:term_id>/swtds', methods=['GET'])(self.process_terms)

    @jwt_required()
    def index(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            params = {
                "is_deleted": False,
                **request.args
            }

            try:    
                if "start_date" in params:
                    params["start_date"] = datetime.strptime(params.get("start_date"), "%m-%d-%Y").date()
                if "end_date" in params:
                    params["end_date"] = datetime.strptime(params.get("end_date"), "%m-%d-%Y").date()
            except Exception:
                raise InvalidDateTimeFormat()

            terms = self.term_service.get_term(
                lambda q, t: q.filter_by(**params).all()
            )

            return self.build_response({"terms": [term.to_dict() for term in terms]}, 200)
        if request.method == 'POST':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot create Term.")

            data = request.json
            required_fields = [
                'name',
                'start_date',
                'end_date',
                'type'
            ]

            self.check_fields(data, required_fields)

            try:
                date_fmt = '%m-%d-%Y'
                start_date = datetime.strptime(data.get('start_date'), date_fmt)
                end_date = datetime.strptime(data.get('end_date'), date_fmt)
            except Exception:
                raise InvalidDateTimeFormat()
            
            term = self.term_service.create_term(
                data.get('name'),
                start_date,
                end_date,
                data.get('type').upper()
            )

            return self.build_response(term.to_dict(), 200)
    
    @jwt_required()
    def handle_term(self, term_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        term = self.term_service.get_term(
            lambda q, t: q.filter_by(id=term_id).first()
        )

        if not term or (term and term.is_deleted):
            raise TermNotFoundError()

        if request.method == 'GET':         
            response = {"data": term.to_dict()}  
            return self.build_response(response, 200)
        if request.method == 'PUT':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update Term.")

            data = {**request.json}

            try:
                date_fmt = '%m-%d-%Y'

                if data.get('start_date'):
                    start_date = datetime.strptime(data.get('start_date'), date_fmt)
                    data['start_date'] = start_date

                if data.get('end_date'):
                    end_date = datetime.strptime(data.get('end_date'), date_fmt)
                    data['end_date'] = end_date
            except Exception:
                raise InvalidDateTimeFormat()
            term = self.term_service.update_term(term, **data)

            return self.build_response(term.to_dict(), 200)
        if request.method == 'DELETE':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete Term.")

            self.term_service.delete_term(term)
            
            return self.build_response({"message": "Term deleted"}, 200)

    @jwt_required()
    def process_terms(self, term_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        term = self.term_service.get_term(
            lambda q, t: q.filter_by(id=term_id).first()
        )
        if not term or (term and term.is_deleted):
            raise TermNotFoundError()
        
        author_id = int(request.args.get('author_id')) if 'author_id' in request.args else None
        
        if not author_id:
            return redirect(url_for('swtd.index', term_id=term.id), code=303)
        else:
            return redirect(url_for('swtd.index', term_id=term.id, author_id=author_id), code=303)

def setup(app: Flask) -> None:
    app.register_blueprint(TermController('term', __name__, url_prefix='/terms'))
