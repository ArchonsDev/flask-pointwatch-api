from flask import jsonify

@staticmethod
def build_response(data, code):
    if code >= 400 and code <= 499:
        return jsonify({'error': data}), code
    
    return jsonify(data), code
