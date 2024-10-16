from typing import Any
from datetime import datetime
import os

from flask import Blueprint, request, Response, Flask, redirect, url_for
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import swtd_service, jwt_service, user_service, auth_service, ft_service, swtd_validation_service, swtd_comment_service, term_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, SWTDFormNotFoundError, MissingRequiredPropertyError, SWTDCommentNotFoundError, TermNotFoundError, AuthenticationError, ProofNotFoundError, UserNotFoundError

class SWTDController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.swtd_service = swtd_service
        self.jwt_service = jwt_service
        self.user_service = user_service
        self.auth_service = auth_service
        self.ft_service = ft_service
        self.swtd_validation_service = swtd_validation_service
        self.swtd_comment_service = swtd_comment_service
        self.term_service = term_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/', methods=['GET', 'POST'])(self.index)
        self.route('/<int:form_id>', methods=['GET', 'PUT', 'DELETE'])(self.process_swtd)
        self.route('/<int:form_id>/comments', methods=['GET', 'POST'])(self.process_comments)
        self.route('/<int:form_id>/comments/<int:comment_id>', methods=['GET', 'PUT', 'DELETE'])(self.handle_comment)
        self.route('/<int:form_id>/proof', methods=['GET', 'POST', 'DELETE'])(self.show_proof)

    @jwt_required()
    def index(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(lambda q, u: q.filter_by(email=email).first())
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            params = {
                "is_deleted": False,
                **request.args
            }

            author = self.user_service.get_user(
                lambda q, u: q.filter_by(id=int(params.get("author_id", 0)), is_deleted=False).first()
            )

            is_author = requester == author
            is_head_of_author = requester == author.department.head
            
            # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
            if not is_head_of_author and not is_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD Forms.")

            try:
                if "start_date" in params:
                    params["start_date"] = datetime.strptime(params.get("start_date"), "%m-%d-%Y").date()
                if "end_date" in params:
                    params["end_date"] = datetime.strptime(params.get("end_date"), "%m-%d-%Y").date()
            except Exception:
                raise InvalidDateTimeFormat()

            swtd_forms = self.swtd_service.get_swtd(
                lambda q, s: q.filter_by(**params)
            )

            response = {
                "data": [{
                    **form.to_dict(),
                    "author": form.author.to_dict(),
                    "comments": [{
                        **c.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, form.comments))],
                    "proof": [{
                        **p.to_dict()
                    } for p in form.proof],
                    "term": form.term.to_dict(),
                    "validator": {
                        **form.validator.to_dict(),
                        "department": {
                            **form.validator.department.to_dict(),
                            "head": form.validator.department.head.to_dict() if form.validator.department.head else None
                        }
                    } if form.validator else None
                } for form in swtd_forms]
            }

            return self.build_response(response, 200)
        elif request.method == 'POST':
            data = request.form
            required_fields = [
                "title",
                "venue",
                "category",
                "start_date",
                "end_date",
                "total_hours",
                "points",
                "benefits",
                "has_deliverables",
                "author_id",
                "term_id"
            ]

            self.check_fields(data, required_fields)

            files = request.files.getlist('files')
            if not files:
                raise MissingRequiredPropertyError("files")
            
            term = self.term_service.get_term(
                lambda q, t: q.filter_by(id=data.get("term_id")).first()
            )
            if not term or (term and term.is_deleted):
                raise TermNotFoundError()

            try:
                start_date = datetime.strptime(data.get("start_date"), "%m-%d-%Y").date()
                end_date = datetime.strptime(data.get("end_date"), "%m-%d-%Y").date()
            except Exception:
                raise InvalidDateTimeFormat()

            print(type(start_date))
            print(start_date)
            print(type(end_date))
            print(end_date)
            
            swtd = self.swtd_service.create_swtd(
                title=data.get("title"),
                venue=data.get("venue"),
                category=data.get("category"),
                start_date=start_date,
                end_date=end_date,
                total_hours=float(data.get("total_hours")),
                points=float(data.get("points")),
                benefits=data.get("benefits"),
                has_deliverables=data.get("has_deliverables").lower() in ("true", "1"),
                author_id=int(data.get("author_id")),
                term_id=term.id,
            )

            for file in files:
                print(f"Saving file... {file.filename}")
                self.ft_service.save(requester.id, swtd.id, file)
                print(f"Saved file to /data/{requester.id}/{swtd.id}/{file.filename}")

            response = {
                "data": {
                    **swtd.to_dict(),
                    "author": swtd.author.to_dict(),
                    "comments": [{
                        **c.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, swtd.comments))],
                    "proof": [{
                        **p.to_dict()
                    } for p in swtd.proof],
                    "term": swtd.term.to_dict(),
                    "validator": {
                        **swtd.validator.to_dict(),
                        "department": {
                            **swtd.validator.department.to_dict(),
                            "head": swtd.validator.department.head.to_dict() if swtd.validator.department.head else None
                        }
                    } if swtd.validator else None
                }
            }

            return self.build_response(response, 200)

    @jwt_required()
    def process_swtd(self, form_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(lambda q, u: q.filter_by(email=email).first())

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id).first())
        if not swtd or (swtd and swtd.is_deleted):
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            is_author = swtd.author == requester
            is_head_of_author = requester == swtd.author.department.head

            if not is_head_of_author and not is_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")
            
            response = {
                "data": {
                    **swtd.to_dict(),
                    "author": swtd.author.to_dict(),
                    "comments": [{
                        **c.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, swtd.comments))],
                    "proof": [{
                        **p.to_dict()
                    } for p in swtd.proof],
                    "term": swtd.term.to_dict(),
                    "validator": {
                        **swtd.validator.to_dict(),
                        "department": {
                            **swtd.validator.department.to_dict(),
                            "head": swtd.validator.department.head.to_dict() if swtd.validator.department.head else None
                        }
                    } if swtd.validator else None
                }
            }

            return self.build_response(response, 200)
        elif request.method == 'PUT':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_head_of_author and not is_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update SWTD form data.")
            
            data = {
                "validation_status": "PENDING",
                **request.json
            }

            try:
                if "start_date" in data:
                    data["start_date"] = datetime.strptime(data.get("start_date"), "%m-%d-%Y")
                if "end_date" in data:
                    data["end_date"] = datetime.strptime(data.get("end_date"), "%m-%d-%Y")
            except Exception:
                raise InvalidDateTimeFormat()

            if "validation_status" in data and data.get("validation_status") != "PENDING":
                if not "validator_id" in data:
                    raise MissingRequiredPropertyError("validator_id")

                validator = self.user_service.get_user(
                    lambda q, u: q.filter_by(id=data.get("validator_id"), is_deleted=False).first()
                )

                if not validator:
                    raise UserNotFoundError()

                data["date_validated"] = datetime.now()

            if "term_id" in data:
                term = self.term_service.get_term(
                    lambda q, t: q.filter_by(id=data.get("term_id"), is_deleted=False).first()
                )

                if not term:
                    raise TermNotFoundError()

            swtd = self.swtd_service.update_swtd(swtd, **data)

            response = {
                "data": {
                    **swtd.to_dict(),
                    "author": swtd.author.to_dict(),
                    "comments": [{
                        **c.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, swtd.comments))],
                    "proof": [{
                        **p.to_dict()
                    } for p in swtd.proof],
                    "term": swtd.term.to_dict(),
                    "validator": {
                        **swtd.validator.to_dict(),
                        "department": {
                            **swtd.validator.department.to_dict(),
                            "head": swtd.validator.department.head.to_dict() if swtd.validator.department.head else None
                        }
                    } if swtd.validator else None
                }
            }

            return self.build_response(response, 200)
        elif request.method == 'DELETE':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_head_of_author and not is_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete SWTD form.")
            
            self.swtd_service.delete_swtd(swtd)
            return self.build_response({"message": "SWTD Form deleted."}, 200)
    
    @jwt_required()
    def process_comments(self, form_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        swtd = self.swtd_service.get_swtd(
            lambda q, s: q.filter_by(id=form_id).first()
        )
        if not swtd or (swtd and swtd.is_deleted):
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form comments.")

            params = {
                "is_deleted": False,
                "swtd_id": swtd.id,
                **request.args
            }

            comments = self.swtd_comment_service.get_comment(
                lambda q, c: q.filter_by(**params).all()
            )

            return self.build_response({
                "data": [{
                    **comment.to_dict(),
                    "author": comment.author.to_dict()
                } for comment in comments]
            }, 200)
        if request.method == 'POST':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot add an SWTD form comment.")

            data = {
                **request.json,
                "author_id": requester.id,
                "swtd_id": form_id
            }
            required_fields = ['message']

            self.check_fields(data, required_fields)
            
            comment = self.swtd_comment_service.create_comment(**data)
            return self.build_response({
                "data": {
                    **comment.to_dict(),
                    "author": comment.author.to_dict()
                }
            }, 200)
    
    @jwt_required()
    def handle_comment(self, form_id: int, comment_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(lambda q, u: q.filter_by(email=email).first())

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        swtd = self.swtd_service.get_swtd(lambda q, t: q.filter_by(id=form_id).first())
        if not swtd or (swtd and swtd.is_deleted):
            raise SWTDFormNotFoundError()
        
        comment = self.swtd_comment_service.get_comment(lambda q, c: q.filter_by(id=comment_id).first())
        if not comment or (comment and comment.is_deleted):
            raise SWTDCommentNotFoundError()
        
        if request.method == 'GET':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form comment.")
            
            return self.build_response({
                "data": {
                    **comment.to_dict(),
                    "author": comment.author.to_dict()
                }
            }, 200)
        if request.method == 'PUT':
            is_author = requester == comment.author

            if not is_author:
                raise InsufficientPermissionsError("Cannot update SWTD form comment.")

            data = {**request.json}

            self.swtd_comment_service.update_comment(comment, **data)
            return redirect(url_for('swtd.process_swtd', form_id=swtd.id), code=303)
        if request.method == 'DELETE':
            is_author = requester == comment.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete SWTD form comment.")
            
            self.swtd_comment_service.delete_comment(comment)
            return self.build_response({"message": "Comment deleted."}, 200)
  
    @jwt_required()
    def show_proof(self, form_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(lambda q, u: q.filter_by(email=email).first())

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        swtd = self.swtd_service.get_swtd(lambda q, s: q.filter_by(id=form_id).first())
        if not swtd or (swtd and swtd.is_deleted):
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form proof.")

            params = {**request.args}
            required_fields = ['id']
            self.check_fields(params, required_fields)

            proof = self.ft_service.get_proof(lambda q, p: q.filter_by(id=params.get("id")).first())
            if not proof:
                raise ProofNotFoundError()

            with open(proof.path, 'rb') as f:
                content = f.read()

            return Response(content, mimetype=proof.content_type, status=200)
        if request.method == 'POST':
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot add SWTD form proof.")
            
            files = request.files.getlist('files')
            if not files:
                raise MissingRequiredPropertyError("files")

            for file in files:
                self.ft_service.save(requester.id, swtd.id, file)

            self.swtd_service.update_swtd(swtd, validation_status="PENDING")
            
            response = {
                "data": {
                    **swtd.to_dict(),
                    "author": swtd.author.to_dict(),
                    "comments": [{
                        **c.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, swtd.comments))],
                    "proof": [{
                        **p.to_dict()
                    } for p in swtd.proof],
                    "term": swtd.term.to_dict(),
                    "validator": {
                        **swtd.validator.to_dict(),
                        "department": {
                            **swtd.validator.department.to_dict(),
                            "head": swtd.validator.department.head.to_dict() if swtd.validator.department.head else None
                        }
                    } if swtd.validator else None
                }
            }

            return self.build_response(response, 200)
        if request.method == "DELETE":
            is_author = requester == swtd.author
            is_head_of_author = requester == swtd.author.department.head

            if not is_author and not is_head_of_author and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete SWTD form proof.")

            params = {**request.args}
            required_fields = ['id']
            self.check_fields(params, required_fields)

            proof = self.ft_service.get_proof(lambda q, p: q.filter_by(id=params.get("id")).first())
            if not proof:
                raise ProofNotFoundError()

            if proof not in swtd.proof:
                raise InsufficientPermissionsError("Cannot delete proof of other SWTDs")

            self.ft_service.delete_proof(proof)
            self.swtd_service.update_swtd(swtd, validation_status="PENDING")
            
            return redirect(url_for('swtd.process_swtd', form_id=swtd.id), code=303)

def setup(app: Flask) -> None:
    app.register_blueprint(SWTDController('swtd', __name__, url_prefix='/swtds'))
