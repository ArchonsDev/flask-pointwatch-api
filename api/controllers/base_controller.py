from flask import jsonify

def build_response(data, code):
    return jsonify(data), code
