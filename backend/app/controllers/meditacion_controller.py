# controllers/meditacion_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.meditacion_service import MeditacionService

meditacion_controller = Blueprint('meditacion_controller', __name__)

@meditacion_controller.route('/meditacion/iniciar', methods=['POST'])
@jwt_required()
def iniciar_meditacion():
    """
    Endpoint para confirmar inicio de sesión en frontend.
    No crea una sesión activa en la base de datos.
    """
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()

        duracion = data.get('duracion', 10)
        tipo_meditacion = data.get('tipo_meditacion', 'mindfulness')

        # Opcional: Validar tipo de meditación aquí si es necesario
        if not MeditacionService.es_tipo_valido(tipo_meditacion):
            return jsonify({'error': 'Tipo de meditación no válido'}), 400

        # Opcional: Verificar si hay otra sesión activa en el frontend
        # Esto se haría con estado en el frontend o tokens expirables
        # No es obligatorio aquí si se maneja en el frontend

        # Simplemente devolver un mensaje de confirmación
        return jsonify({'message': 'Inicio de meditación confirmado en frontend', 'duracion': duracion, 'tipo_meditacion': tipo_meditacion}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meditacion_controller.route('/meditacion/guardar', methods=['POST'])
@jwt_required()
def guardar_meditacion():
    """
    Endpoint para guardar los datos de una sesión de meditación finalizada desde el frontend.
    """
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()

        # Validar campos requeridos
        campos_requeridos = ['tecnica_id', 'duracion_planificada', 'duracion_real', 'tipo_meditacion', 'estado']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({'error': f'Falta el campo requerido: {campo}'}), 400

        # Extraer datos
        tecnica_id = data.get('tecnica_id')
        duracion_planificada = data.get('duracion_planificada')
        duracion_real = data.get('duracion_real')
        tipo_meditacion = data.get('tipo_meditacion')
        estado = data.get('estado') # 'Completado' o 'Cancelado'
        calificacion = data.get('calificacion') # Opcional

        # Opcional: Validar estado
        if estado not in ['Completado', 'Cancelado']:
             return jsonify({'error': 'Estado no válido. Debe ser Completado o Cancelado'}), 400

        # Llamar al servicio para crear la sesión
        resultado = MeditacionService.guardar_sesion_finalizada(
            usuario_id=usuario_id,
            tecnica_id=tecnica_id,
            duracion_planificada=duracion_planificada,
            duracion_real=duracion_real,
            tipo_meditacion=tipo_meditacion,
            estado=estado,
            calificacion=calificacion
        )

        return jsonify({'message': 'Sesión de meditación guardada exitosamente', 'sesion': resultado}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener historial (no cambia)
@meditacion_controller.route('/meditacion/historial', methods=['GET'])
@jwt_required()
def obtener_historial():
    try:
        usuario_id = get_jwt_identity()
        limite = request.args.get('limite', 20, type=int)
        historial = MeditacionService.obtener_historial_meditaciones(usuario_id, limite)
        return jsonify(historial), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener tipos de meditación (no cambia)
@meditacion_controller.route('/meditacion/tipos', methods=['GET'])
def obtener_tipos():
    tipos = MeditacionService.obtener_tipos_meditacion()
    return jsonify(tipos), 200
