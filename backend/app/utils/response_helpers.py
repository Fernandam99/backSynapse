from flask import jsonify

def success_response(data=None, message="Operación exitosa", status_code=200):
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error interno del servidor", status_code=500, error_code=None):
    response = {
        'success': False,
        'message': message
    }
    if error_code:
        response['error_code'] = error_code
    return jsonify(response), status_code

def validation_error_response(errors, message="Errores de validación"):
    return jsonify({
        'success': False,
        'message': message,
        'errors': errors
    }), 400
