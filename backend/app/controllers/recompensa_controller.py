# controllers/recompensa_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.recompensa_service import RecompensaService

recompensa_controller = Blueprint('recompensa_controller', __name__)

@recompensa_controller.route('/recompensas/verificar-automaticas', methods=['POST'])
@jwt_required()
def verificar_recompensas_automaticas():
    try:
        usuario_id = get_jwt_identity()
        resultado = RecompensaService.verificar_todas_recompensas_usuario(usuario_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500