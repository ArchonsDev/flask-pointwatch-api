from typing import Any
from datetime import datetime, date

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..schemas.term_schema import CreateTermSchema, UpdateTermSchema
from ..services import jwt_service, user_service, term_service, auth_service

from ..exceptions.authorization import AuthorizationError
from ..exceptions.resource import ResourceNotFoundError,TermNotFoundError
from ..exceptions.validation import InvalidDateTimeFormat, InvalidParameterError

class TermController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.term_service = term_service
        self.auth_service = auth_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('', methods=['GET'])(self.get_all_terms)
        self.route('', methods=['POST'])(self.create_term)
        self.route('/<int:term_id>', methods=['GET'])(self.get_term)
        self.route('/<int:term_id>', methods=['PUT'])(self.update_term)
        self.route('/<int:term_id>', methods=['DELETE'])(self.delete_term)
        self.route('/<int:term_id>/<field_name>', methods=['GET'])(self.get_term_property)

    @jwt_required()
    def get_all_terms(self) -> Response:
        requester = self.jwt_service.get_requester()

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

        terms = self.term_service.get_term(lambda q, t: q.filter_by(**params).all())
        return self.build_response({"terms": [t.to_dict() for t in terms]}, 200)

    @jwt_required()
    def create_term(self) -> Response:
        requester = self.jwt_service.get_requester()

        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot create Term.")

        data = self.parse_form(request.json, CreateTermSchema)

        try:
            date_fmt = '%m-%d-%Y'
            start_date = datetime.strptime(data.get('start_date'), date_fmt)
            end_date = datetime.strptime(data.get('end_date'), date_fmt)
        except Exception:
            raise InvalidDateTimeFormat()
        
        term = self.term_service.create_term(
            name=data.get('name'),
            start_date=start_date,
            end_date=end_date,
            type=data.get('type').strip().upper()
        )

        return self.build_response({"term": term.to_dict()}, 200)

    @jwt_required()
    def get_term(self, term_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=term_id, is_deleted=False).first())
        if not term: raise TermNotFoundError()

        return self.build_response({"term": term.to_dict()}  , 200)
    
    @jwt_required()
    def update_term(self, term_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=term_id, is_deleted=False).first())
        if not term: raise TermNotFoundError()

        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot update Term.")

        data = self.parse_form(request.json, UpdateTermSchema)

        try:
            if 'start_date' in data:
                data['start_date'] = datetime.strptime(data.get('start_date'), '%m-%d-%Y')

            if 'end_date' in data:
                data['end_date'] = datetime.strptime(data.get('end_date'), '%m-%d-%Y')
        except Exception:
            raise InvalidDateTimeFormat()

        if 'type' in data:
            data['type'] = data.get('type', '').strip().upper()

        term = self.term_service.update_term(term, **data)
        return self.build_response({"term": term.to_dict()}, 200)

    @jwt_required()
    def delete_term(self, term_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=term_id, is_deleted=False).first())
        if not term: raise TermNotFoundError()

        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot delete Term.")

        self.term_service.delete_term(term)
        return self.build_response({"message": "Term deleted"}, 200)

    @jwt_required()
    def get_term_property(self, term_id: int, field_name: str) -> Response:
        requester = self.jwt_service.get_requester()
        
        term = self.term_service.get_term(lambda q, t: q.filter_by(id=term_id, is_deleted=False).first())
        if not term: raise TermNotFoundError()

        protected_fields = ["swtd_forms", "clearances"]
        if field_name in protected_fields and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError(f"Cannot retreive data for term {field_name}.")
        
        if not hasattr(term, field_name): raise ResourceNotFoundError()

        prop = getattr(term, field_name, None)
        use_list = isinstance(prop, list)

        response = {}
        try:
            if use_list:
                prop = list(filter(lambda i: hasattr(i, 'is_deleted') and i.is_deleted == False, prop))

            response[field_name] = [o.to_dict() for o in prop] if use_list else prop.to_dict()
        except AttributeError:
            if isinstance(prop, datetime):
                response[field_name] = prop.strftime("%m-%d-%Y %H:%M")
            elif isinstance(prop, date):
                response[field_name] = prop.strftime("%m-%d-%Y")
            else:
                response[field_name] = prop

        return self.build_response(response, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(TermController('term', __name__, url_prefix='/terms'))
