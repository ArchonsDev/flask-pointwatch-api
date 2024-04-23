from flask import jsonify

def build_response(response, code):
    if code >= 400 and code <= 599:
        return jsonify({"error": response}), code
    
    return jsonify(response), code
