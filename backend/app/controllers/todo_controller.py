# controllers/todo_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.todo_service import TodoService
from app.services.recompensa_service import RecompensaService

todo_controller = Blueprint('todo_controller', __name__)

@todo_controller.route('/todo/listas', methods=['GET'])
@jwt_required()
def obtener_listas_todo():
    try:
        usuario_id = get_jwt_identity()
        listas = TodoService.obtener_listas_usuario(usuario_id)
        return jsonify(listas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
