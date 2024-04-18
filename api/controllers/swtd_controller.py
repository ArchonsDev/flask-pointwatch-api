from flask import jsonify, Blueprint, request
from app import app
from swtd_service import create_entry, get_entry, update_entry, delete_entry
from base_controller import build_response

swtd_bp = Blueprint('swtd', __name__, url_prefix='/form')

@swtd_bp.route('/create', methods=['POST'])
def create_form_entry():
    data = request.json
    response, code = create_entry(**data)
    return build_response(response, code)

@swtd_bp.route('/<int:entry_id>', methods=['GET'])
def get_form_entry(entry_id):
    entry = get_entry(entry_id)
    if entry:
        return jsonify(entry)
    else:
        return jsonify({'error': 'Entry not found'}), 404

@swtd_bp.route('/<int:entry_id>', methods=['PUT'])
def update_form_entry(entry_id):
    data = request.json
    response, code = update_entry(entry_id, **data)
    return build_response(response, code)

@swtd_bp.route('/<int:entry_id>', methods=['DELETE'])
def delete_form_entry(entry_id):
    response, code = delete_entry(entry_id)
    return build_response(response, code)

app.register_blueprint(swtd_bp)
