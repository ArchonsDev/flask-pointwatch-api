from flask import jsonify, Response

def build_response(data, code):
    if code >= 400 and code <= 499:
        return Response(jsonify({'error': data}), status=code, mimetype='application/json')
    
    return Response(jsonify(data), status=code, mimetype='application/json')
