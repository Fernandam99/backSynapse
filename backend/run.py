from backend.app import create_app
from backend.models import db
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask import jsonify

# Cargar variables de entorno desde .env
load_dotenv()

# Crear la aplicación usando la variable FLASK_ENV o 'development' por defecto
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Inicializar migraciones con la app y la base de datos
migrate = Migrate(app, db)

@app.route('/')
def index():
    return jsonify({
        'message': 'Synapse API está funcionando correctamente',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'usuarios': '/api/usuarios',
            'salas': '/api/salas',
            'tareas': '/api/tareas',
            'sesiones': '/api/sesiones',
            'tecnicas': '/api/tecnicas',
            'recompensas': '/api/recompensas',
            'progreso': '/api/progreso'
        }
    })

@app.route('/health')
def health_check():
    try:
        # Verificar conexión a la base de datos
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
