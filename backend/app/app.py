from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager  

from app.models import db
from app.config import Config

# Importación rutas
from app.routes.auth import auth_bp
from app.routes.progreso_routes import progreso_bp
from app.routes.recompensa_routes import recompensa_bp
from app.routes.sala_routes import sala_bp
from app.routes.sesion_routes import sesion_bp
from app.routes.tarea_routes import tarea_bp
from app.routes.tecnica_routes import tecnica_bp
from app.routes.usuario_routes import usuario_bp

def create_app():
    app = Flask(__name__)
    
    # Carga configuración
    app.config.from_object(Config)

    # Inicializa extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)  # Si usas JWT

    # Configura CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # Registra blueprints con prefijos consistentes en plural (opcional)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(progreso_bp, url_prefix='/api/progresos')
    app.register_blueprint(recompensa_bp, url_prefix='/api/recompensas')
    app.register_blueprint(sala_bp, url_prefix='/api/salas')
    app.register_blueprint(sesion_bp, url_prefix='/api/sesiones')
    app.register_blueprint(tarea_bp, url_prefix='/api/tareas')
    app.register_blueprint(tecnica_bp, url_prefix='/api/tecnicas')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')

    # Crear tablas y datos base al iniciar la app
    with app.app_context():
        db.create_all()
        # Aquí puedes agregar inicialización de roles, técnicas y recompensas

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

