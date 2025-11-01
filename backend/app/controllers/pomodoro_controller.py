# controllers/pomodoro_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.pomodoro_service import PomodoroService
from app.services.recompensa_service import RecompensaService

pomodoro_controller = Blueprint('pomodoro_controller', __name__)

@pomodoro_controller.route('/pomodoro/iniciar', methods=['POST'])
@jwt_required()
def iniciar_pomodoro():
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()

        duracion_trabajo = data.get('duracion_trabajo', 25)
        duracion_descanso = data.get('duracion_descanso', 5)
        ciclos_objetivo = data.get('ciclos_objetivo', 4)
        modo_no_distraccion = data.get('modo_no_distraccion', False)

        pomodoro = PomodoroService.iniciar_pomodoro(usuario_id, duracion_trabajo, duracion_descanso, ciclos_objetivo, modo_no_distraccion)

        return jsonify({'message': 'Pomodoro iniciado exitosamente', 'pomodoro': pomodoro}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Similar structure for other routes like completar_ciclo_pomodoro, finalizar_pomodoro, obtener_estado_pomodoro
