from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import build_response, check_fields
from ..services import jwt_service, user_service, term_service, auth_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat

term_bp = Blueprint('term', __name__, url_prefix='/terms')

@term_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def index():
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)

    if request.method == 'GET':
        terms = term_service.get_all_terms()

        return build_response({"terms": [term.to_dict() for term in terms]}, 200)
    if request.method == 'POST':
        data = request.json
        required_fields = [
            'name',
            'start_date',
            'end_date'
        ]

        check_fields(data, required_fields)

        if not auth_service.has_permissions(requester, minimum_auth='admin'):
            raise InsufficientPermissionsError("Cannot create Term,")
        
        try:
            date_fmt = '%m-%d-%Y'
            start_date = datetime.strptime(data.get('start_date'), date_fmt)
            end_date = datetime.strptime(data.get('end_date'), date_fmt)
        except Exception:
            raise InvalidDateTimeFormat()
        
        term = term_service.create_term(
            data.get('name'),
            start_date,
            end_date
        )

        return build_response(term.to_dict(), 200)
