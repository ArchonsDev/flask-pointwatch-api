from typing import Any
from datetime import datetime, date

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController

from ..exceptions.authorization import AuthorizationError
from ..exceptions.resource import SWTDFormNotFoundError, UserNotFoundError, TermNotFoundError, SWTDCommentNotFoundError, ProofNotFoundError
from ..exceptions.validation import MissingRequiredParameterError, InvalidDateTimeFormat, InvalidParameterError

from ..services import swtd_service, jwt_service, user_service, auth_service, ft_service, swtd_comment_service, term_service

class SWTDController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.swtd_service = swtd_service
        self.jwt_service = jwt_service
        self.user_service = user_service
        self.auth_service = auth_service
        self.ft_service = ft_service
        self.swtd_comment_service = swtd_comment_service
        self.term_service = term_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('', methods=['GET'])(self.get_all_swtds)
        self.route('', methods=['POST'])(self.create_swtd)
        self.route('/<int:form_id>', methods=['GET'])(self.get_swtd)
        self.route('/<int:form_id>', methods=['PUT'])(self.update_swtd)
        self.route('/<int:form_id>', methods=['DELETE'])(self.delete_swtd)
        self.route('/<int:form_id>/<field_name>', methods=['GET'])(self.get_swtd_property)
        self.route('/<int:form_id>/comments', methods=['POST'])(self.create_swtd_comment)
        self.route('/<int:form_id>/comments/<int:comment_id>', methods=['GET'])(self.get_swtd_comment)
        self.route('/<int:form_id>/comments/<int:comment_id>', methods=['PUT'])(self.update_swtd_comment)
        self.route('/<int:form_id>/comments/<int:comment_id>', methods=['DELETE'])(self.delete_swtd_comment)
        self.route('/<int:form_id>/proof', methods=['POST'])(self.add_swtd_proof)
        self.route('/<int:form_id>/proof/<int:proof_id>', methods=['GET'])(self.show_proof)
        self.route('/<int:form_id>/proof/<int:proof_id>', methods=['DELETE'])(self.delete_swtd_proof)

    @jwt_required()
    def get_all_swtds(self) -> Response:
        requester = self.jwt_service.get_requester()

        params = {"is_deleted": False, **request.args}

        author = self.user_service.get_user(lambda q, u: q.filter_by(id=int(params.get("author_id", 0)), is_deleted=False).first())
        
        # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
        if not author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve SWTD Forms.")

        try:
            if "start_date" in params:
                params["start_date"] = datetime.strptime(params.get("start_date"), "%m-%d-%Y").date()
            if "end_date" in params:
                params["end_date"] = datetime.strptime(params.get("end_date"), "%m-%d-%Y").date()
        except Exception:
            raise InvalidDateTimeFormat()

        swtd_forms = self.swtd_service.get_swtd(lambda q, s: q.filter_by(**params).all())
        return self.build_response({"swtd_forms": [f.to_dict() for f in swtd_forms]}, 200)

    @jwt_required()
    def create_swtd(self) -> Response:
        requester = self.jwt_service.get_requester()

        data = {**request.form}
        required_fields = [
            "title",
            "venue",
            "category",
            "start_date",
            "end_date",
            "total_hours",
            "points",
            "benefits",
            "term_id"
        ]

        self.check_fields(data, required_fields)

        files = request.files.getlist('files')
        if not files: raise MissingRequiredParameterError("files")

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=data.get("term_id"), is_deleted=False).first())
        if not term: raise TermNotFoundError()

        try:
            start_date = datetime.strptime(data.get("start_date"), "%m-%d-%Y").date()
            end_date = datetime.strptime(data.get("end_date"), "%m-%d-%Y").date()
        except Exception:
            raise InvalidDateTimeFormat()
        
        swtd = self.swtd_service.create_swtd(
            title=data.get("title"),
            venue=data.get("venue"),
            category=data.get("category"),
            start_date=start_date,
            end_date=end_date,
            total_hours=float(data.get("total_hours")),
            points=float(data.get("points")),
            benefits=data.get("benefits"),
            author=requester,
            term=term
        )

        for file in files: self.ft_service.save(requester.id, swtd.id, file)
        return self.build_response({"swtd_form": swtd.to_dict()}, 200)

    @jwt_required()
    def get_swtd(self, form_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve SWTD form data.")

        return self.build_response({"swtd_form": swtd.to_dict()}, 200)

    @jwt_required()
    def update_swtd(self, form_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot update SWTD form data.")
        
        allowed_fields = [
            'is_deleted',
            'title',
            'venue',
            'category',
            'start_date',
            'end_date',
            'total_hours',
            'points',
            'benefits',
            'validation_status',
            'term_id'
        ]
        data = {"validation_status": "PENDING", **request.json}

        if not all(key in allowed_fields for key in data.keys()):
            raise InvalidParameterError()
        
        if 'is_deleted' in data and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot change SWTDForm deletion state.")

        try:
            if "start_date" in data:
                data["start_date"] = datetime.strptime(data.get("start_date"), "%m-%d-%Y")
            if "end_date" in data:
                data["end_date"] = datetime.strptime(data.get("end_date"), "%m-%d-%Y")
        except Exception:
            raise InvalidDateTimeFormat()

        if "validation_status" in data:
            status = data.get("validation_status")

            if status == "PENDING":
                data["validator"] = None
                data["date_validated"] = None
            else:
                if not "validator_id" in data:
                    raise MissingRequiredParameterError("validator_id")
                
                validator_id = data.get("validator_id", 0)
                validator = self.user_service.get_user(lambda q, u: q.filter_by(id=validator_id, is_deleted=False).first())
                if not validator: raise UserNotFoundError()

                data["validator"] = validator
                data["date_validated"] = datetime.now()

        if "term_id" in data:
            term = self.term_service.get_term(lambda q, t: q.filter_by(id=data.get("term_id"), is_deleted=False).first())
            if not term: raise TermNotFoundError()

        swtd = self.swtd_service.update_swtd(swtd, **data)
        return self.build_response({"swtd_form": swtd.to_dict()}, 200)

    @jwt_required()
    def delete_swtd(self, form_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot delete SWTD form.")
        
        self.swtd_service.delete_swtd(swtd)
        return self.build_response({"message": "SWTD Form deleted."}, 200)

    @jwt_required()
    def get_swtd_property(self, form_id: int, field_name: str) -> Response:
        requester = self.jwt_service.get_requester()
        
        swtd = self.swtd_service.get_swtd(lambda q, t: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError(f"Cannot retreive data for SWTDForm {field_name}.")
        
        prop = getattr(swtd, field_name, None)
        use_list = isinstance(prop, list)

        response = {}
        try:
            response[field_name] = [o.to_dict() for o in prop] if use_list else prop.to_dict()
        except AttributeError:
            if isinstance(prop, datetime):
                response[field_name] = prop.strftime("%m-%d-%Y %H:%M")
            elif isinstance(prop, date):
                response[field_name] = prop.strftime("%m-%d-%Y")
            else:
                response[field_name] = prop

        return self.build_response(response, 200)

    @jwt_required()
    def create_swtd_comment(self, form_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot add an SWTD form comment.")

        data = {**request.json, "author_id": requester.id, "swtd_id": swtd.id}
        required_fields = ['message']

        self.check_fields(data, required_fields)
        
        comment = self.swtd_comment_service.create_comment(**data)
        return self.build_response({"comment": comment.to_dict()}, 200)

    @jwt_required()
    def get_swtd_comment(self, form_id: int, comment_id: int) -> Response:
        requester = self.jwt_service.get_requester()
        
        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot get SWTDForm comment data.")
        
        comment = self.swtd_comment_service.get_comment(lambda q, c: q.filter_by(id=comment_id, is_deleted=False).first())
        if not comment or comment not in swtd.comments: raise SWTDCommentNotFoundError()

        return self.build_response({"comment": comment.to_dict()}, 200)

    @jwt_required()
    def update_swtd_comment(self, form_id: int, comment_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        allowed_fields = ["message"]
        data = {**request.json}
        if not all(key in allowed_fields for key in data.items()):
            raise InvalidParameterError()

        if "message" not in data: raise MissingRequiredParameterError("message")
        
        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        comment = self.swtd_comment_service.get_comment(lambda q, c: q.filter_by(id=comment_id, is_deleted=False).first())
        if not comment or comment not in swtd.comments: raise SWTDCommentNotFoundError()

        if requester != comment.author: raise AuthorizationError("Cannot update comment data.")
        
        comment = self.swtd_comment_service.update_comment(comment, **data)
        return self.build_response({"comment": comment.to_dict()}, 200)
    
    @jwt_required()
    def delete_swtd_comment(self, form_id: int, comment_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        comment = self.swtd_comment_service.get_comment(lambda q, c: q.filter_by(id=comment_id, is_deleted=False).first())
        if not comment or comment not in swtd.comments: raise SWTDCommentNotFoundError()

        if requester != comment.author:
            raise AuthorizationError("Cannot delete comment.")
        
        comment = self.swtd_comment_service.delete_comment(comment)
        return self.build_response({"message": "Comment deleted."}, 200)
    
    @jwt_required()
    def add_swtd_proof(self, form_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot add SWTD form proof.")
        
        files = request.files.getlist('files')
        if not files: raise MissingRequiredParameterError("files")

        proofs = []
        for file in files:
            proof = self.ft_service.save(requester.id, swtd.id, file)
            proofs.append(proof)

        swtd = self.swtd_service.update_swtd(swtd, validation_status="PENDING")

        return self.build_response({"proof": [p.to_dict() for p in proofs]}, 200)
  
    @jwt_required()
    def show_proof(self, form_id: int, proof_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve SWTD form proof.")

        proof = self.ft_service.get_proof(lambda q, p: q.filter_by(id=proof_id).first())
        if not proof: raise ProofNotFoundError()

        with open(proof.path, 'rb') as f: content = f.read()
        return Response(content, mimetype=proof.content_type, status=200)
       
    @jwt_required()
    def delete_swtd_proof(self, form_id: int, proof_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id, is_deleted=False).first())
        if not swtd: raise SWTDFormNotFoundError()

        if not requester.is_head_of(swtd.author) and requester != swtd.author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot delete SWTD form proof.")

        proof = self.ft_service.get_proof(lambda q, p: q.filter_by(id=proof_id).first())
        if not proof: raise ProofNotFoundError()

        if proof not in swtd.proof: raise AuthorizationError("Cannot delete proof of other SWTDs")

        self.ft_service.delete_proof(proof)
        self.swtd_service.update_swtd(swtd, validation_status="PENDING")

        return self.build_response({"message": "Proof deleted."}, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(SWTDController('swtd', __name__, url_prefix='/swtds'))
