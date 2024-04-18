from flask import jsonify, request
from app import app
from swtd_service import SWTDService

@app.route('/form', methods=['POST'])
def create_entry():
    data = request.json
    new_entry = SWTDService.create_entry(**data)
    return jsonify(new_entry), 201

@app.route('/form/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    entry = SWTDService.get_entry(entry_id)
    if entry:
        return jsonify(entry)
    else:
        return jsonify({'message': 'Entry not found'}), 404

@app.route('/form/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = request.json
    updated_entry = SWTDService.update_entry(entry_id, **data)
    return jsonify(updated_entry)

@app.route('/form/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    SWTDService.delete_entry(entry_id)
    return '', 204
