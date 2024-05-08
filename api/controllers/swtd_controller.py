import os

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import BaseController
from ..services import swtd_service, jwt_service, user_service, auth_service, ft_service, swtd_validation_service, swtd_comment_service, term_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, SWTDFormNotFoundError, MissingRequiredPropertyError, SWTDCommentNotFoundError, TermNotFoundError

class SWTDController(Blueprint, BaseController):
    def __init__(self, name, import_name, **kwargs):
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

    def map_routes(self):
        self.route('/', methods=['GET', 'POST'])(self.index)
        self.route('/<int:form_id>', methods=['GET', 'PUT', 'DELETE'])(self.process_swtd)
        self.route('/<int:form_id>/comments', methods=['GET', 'POST'])(self.process_comments)
        self.route('/<int:form_id>/comments/<int:comment_id>', methods=['GET', 'PUT', 'DELETE'])(self.handle_comment)
        self.route('/<int:form_id>/validation', methods=['GET', 'PUT'])(self.process_validation)
        self.route('/<int:form_id>/validation/proof', methods=['GET', 'PUT'])(self.show_proof)

    @jwt_required()
    def index(self):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if request.method == 'GET':
            params = {"is_deleted": False, **request.args}
            author_id = int(params.get('author_id', 0))
            # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
            if requester.id != author_id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD Forms.")
            
            swtds = [swtd.to_dict() for swtd in self.swtd_service.get_all_swtds(params=params)]
            return self.build_response({"swtds": swtds}, 200)
        elif request.method == 'POST':
            data = request.form
            required_fields = [
                'author_id',
                'title',
                'category',
                'venue',
                'role',
                'date',
                'time_started',
                'time_finished',
                'points',
                'benefits',
                'term_id'
            ]

            self.check_fields(data, required_fields)

            if len(request.files) != 1:
                raise MissingRequiredPropertyError("proof")

            try:
                data = {
                    **data,
                    'date': datetime.strptime(data.get('date'), '%m-%d-%Y').date(),
                    'time_started': datetime.strptime(data.get('time_started'), '%H:%M').time(),
                    'time_finished': datetime.strptime(data.get('time_finished'), '%H:%M').time()
                }
            except Exception:
                raise InvalidDateTimeFormat()
            
            term = self.term_service.get_term(data.get('term_id'))
            if not term:
                raise TermNotFoundError()
            
            swtd = self.swtd_service.create_swtd(
                data.get('author_id'),
                data.get('title'),
                data.get('venue'),
                data.get('category'),
                data.get('role'),
                data.get('date'),
                data.get('time_started'),
                data.get('time_finished'),
                data.get('points'),
                data.get('benefits'),
                term
            )

            file = request.files.get('proof')

            self.swtd_validation_service.create_validation(swtd, file.filename)
            self.ft_service.save(requester.id, swtd.id, file)

            return self.build_response(swtd.to_dict(), 200)

    @jwt_required()
    def process_swtd(self, form_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        swtd = self.swtd_service.get_swtd(form_id)
        if not swtd:
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")
            
            return self.build_response(swtd.to_dict(), 200)
        elif request.method == 'PUT':
            data = request.json

            try:
                data = {
                    **data,
                    'date': datetime.strptime(data.get('date'), '%m-%d-%Y').date(),
                    'time_started': datetime.strptime(data.get('time_started'), '%H:%M').time(),
                    'time_finished': datetime.strptime(data.get('time_finished'), '%H:%M').time()
                }
            except Exception:
                raise InvalidDateTimeFormat()

            if swtd.author_id != requester.id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update SWTD form data.")
            
            swtd = self.swtd_service.update_swtd(swtd, **data)
            self.swtd_validation_service.update_validation(swtd, requester, valid="PENDING")
            return self.build_response(swtd.to_dict(), 200)
        elif request.method == 'DELETE':
            if swtd.author_id != requester.id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete SWTD form.")
            
            self.swtd_service.delete_swtd(swtd)
            return self.build_response({"message": "SWTD Form deleted."}, 200)
    
    @jwt_required()
    def process_comments(self, form_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        swtd = self.swtd_service.get_swtd(form_id)
        if not swtd:
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form comments.")
            
            comments = swtd.comments
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                comments = list(filter(lambda comment: comment.is_deleted == False, comments))

            return self.build_response({"comments": [comment.to_dict() for comment in comments]}, 200)
        if request.method == 'POST':
            data = request.json
            required_fields = ['message']

            self.check_fields(data, required_fields)

            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot add an SWTD form comment.")
            
            self.swtd_comment_service.create_comment(swtd, requester, data.get('message'))
            return self.build_response({"comments": [comment.to_dict() for comment in swtd.comments]}, 200)
    
    @jwt_required()
    def handle_comment(self, form_id, comment_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        swtd = self.swtd_service.get_swtd(form_id)
        if not swtd:
            raise SWTDFormNotFoundError()
        
        comment = self.swtd_comment_service.get_comment_by_id(comment_id)
        if not comment:
            raise SWTDCommentNotFoundError()
        
        if request.method == 'GET':
            if (comment.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form comment.")
            
            return self.build_response(comment.to_dict(), 200)
        if request.method == 'PUT':
            data = request.json
            required_fields = ['message']

            if comment.author_id != requester.id:
                raise InsufficientPermissionsError("Cannot update SWTD form comment.")

            self.check_fields(data, required_fields)

            self.swtd_comment_service.update_comment(comment, data.get('message'))
            return self.build_response(comment.to_dict(), 200)
        if request.method == 'DELETE':
            if (comment.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete SWTD form comment.")
            
            self.swtd_comment_service.delete_comment(comment)
            return self.build_response({"message": "Comment deleted."}, 200)
    
    @jwt_required()
    def process_validation(self, form_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        swtd = self.swtd_service.get_swtd(form_id)
        if not swtd:
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")
            
            return self.build_response(swtd.validation.to_dict(), 200)
        if request.method == 'PUT':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")

            data = request.json
            if not 'status' in data:
                raise MissingRequiredPropertyError('status')
            
            if data.get('status') == 'APPROVED':
                self.swtd_validation_service.update_validation(swtd, requester, valid=True)
            elif data.get('status') == 'REJECTED':
                self.swtd_validation_service.update_validation(swtd, requester, valid=False)
            else:
                raise MissingRequiredPropertyError('status')

            return self.build_response(swtd.validation.to_dict(), 200) # TODO: Verify this is updated.

    @jwt_required()
    def show_proof(self, form_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        swtd = self.swtd_service.get_swtd(form_id)
        if not swtd:
            raise SWTDFormNotFoundError()

        if request.method == 'GET':
            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve SWTD form proof.")

            fp = os.path.join(self.ft_service.data_dir, str(swtd.author.id), str(swtd.id), swtd.validation.proof)

            with open(fp, 'rb') as f:
                content = f.read()
                content_type = self.ft_service.get_file_type(swtd.validation.proof)

            return Response(content, mimetype=content_type, status=200)
        if request.method == 'PUT':
            if (swtd.author_id != requester.id or swtd.is_deleted) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update SWTD form proof.")
            
            if len(request.files) != 1:
                raise MissingRequiredPropertyError("proof")
            
            file = request.files.get('proof')

            self.swtd_validation_service.update_proof(swtd, file)
            self.ft_service.save(requester.id, swtd.id, file)

            return self.build_response(swtd.to_dict(), 200)

def setup(app):
    app.register_blueprint(SWTDController('swtd', __name__, url_prefix='/swtds'))
