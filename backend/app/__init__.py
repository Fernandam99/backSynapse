from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .config import Config, DevelopmentConfig, ProductionConfig 
from .models import db

# Routers
from .routes.auth import auth_bp
from .routes.usuario_routes import usuario_bp
from .routes.sala_routes import sala_bp
from .routes.tarea_routes import tarea_bp
from .routes.sesion_routes import sesion_bp
from .routes.tecnica_routes import tecnica_bp
from .routes.recompensa_routes import recompensa_bp
from .routes.progreso_routes import progreso_bp

# Controllers
from .controllers.pomodoro_controller import pomodoro_controller
from .controllers.meditacion_controller import meditacion_controller
from .controllers.todo_controller import todo_controller
from .controllers.recompensa_controller import recompensa_controller

def create_app(config_name='development'):
    app = Flask(__name__)

    # Cargar configuración
    if config_name == "development":
        app.config.from_object(DevelopmentConfig)
    elif config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(sala_bp, url_prefix='/api/salas')
    app.register_blueprint(tarea_bp, url_prefix='/api/tareas')
    app.register_blueprint(sesion_bp, url_prefix='/api/sesiones')
    app.register_blueprint(tecnica_bp, url_prefix='/api/tecnicas')
    app.register_blueprint(recompensa_bp, url_prefix='/api/recompensas')
    app.register_blueprint(progreso_bp, url_prefix='/api/progreso')

    app.register_blueprint(pomodoro_controller, url_prefix='/api/productividad')
    app.register_blueprint(meditacion_controller, url_prefix='/api/bienestar')
    app.register_blueprint(todo_controller, url_prefix='/api/productividad')
    app.register_blueprint(recompensa_controller, url_prefix='/api/gamificacion')

    # Crear tablas, roles, técnicas base y recompensas base
    with app.app_context():
        db.create_all()

        # Crear roles si no existen
        from .models import Rol, Tecnica
        if not Rol.query.first():
            admin_role = Rol(nombre='administrador')
            user_role = Rol(nombre='usuario')
            db.session.add_all([admin_role, user_role])
            db.session.commit()

        # Inicializar técnicas base
        tecnicas_base = [
            {'nombre': 'Pomodoro', 'categoria': 'productividad'},
            {'nombre': 'Meditación', 'categoria': 'bienestar'},
            {'nombre': 'Estudio Tradicional', 'categoria': 'educativo'},
            {'nombre': 'Descanso Activo', 'categoria': 'bienestar'}
        ]
        for tecnica_data in tecnicas_base:
            tecnica_existente = Tecnica.query.filter_by(nombre=tecnica_data['nombre']).first()
            if not tecnica_existente:
                nueva_tecnica = Tecnica(
                    nombre=tecnica_data['nombre'],
                    categoria=tecnica_data['categoria']
                )
                db.session.add(nueva_tecnica)
        db.session.commit()

        # Inicializar recompensas base del sistema
        from app.services.recompensa_service import RecompensaService
        RecompensaService.inicializar_recompensas_sistema()

    return app
