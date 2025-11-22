# backend/tests/conftest.py
import os
import sys
import pytest
from app import create_app
from app.models import db as _db, Rol, Usuario, Tecnica
from werkzeug.security import generate_password_hash

# 🔥 FORZAR entorno de prueba antes de importar app
os.environ.clear()
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_DEBUG'] = 'False'

# Ahora sí importar la app
from app import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()

        # Roles
        roles = ['administrador', 'usuario']
        for nombre in roles:
            if not _db.session.query(Rol).filter_by(nombre=nombre).first():
                _db.session.add(Rol(nombre=nombre))
        _db.session.commit()

        # Usuario de prueba
        rol_admin = _db.session.query(Rol).filter_by(nombre='administrador').first()
        test_user = Usuario(
            username='testuser',
            correo='test@example.com',
            password=generate_password_hash('SecurePass123!'),
            rol_id=rol_admin.id,
            activo=True
        )
        _db.session.add(test_user)
        _db.session.commit()

        # Técnicas esenciales
        if not _db.session.query(Tecnica).first():
            _db.session.add(Tecnica(nombre='Pomodoro'))
            _db.session.add(Tecnica(nombre='Meditación'))
            _db.session.commit()

        yield app

        # Limpiar DB
        _db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    login_resp = client.post('/api/auth/login', json={
        'correo': 'test@example.com',
        'password': 'SecurePass123!'
    })
    token = login_resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}