# controllers/meditacion_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.meditacion_service import MeditacionService
from app.services.recompensa_service import RecompensaService

meditacion_controller = Blueprint('meditacion_controller', __name__)

@meditacion_controller.route('/meditacion/iniciar', methods=['POST'])
@jwt_required()
def iniciar_meditacion():
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()

        duracion = data.get('duracion', 10)
        tipo_meditacion = data.get('tipo_meditacion', 'mindfulness')

        meditacion = MeditacionService.iniciar_meditacion(usuario_id, duracion, tipo_meditacion)

        return jsonify({'message': 'Meditación iniciada exitosamente', 'meditacion': meditacion}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
