import os
from datetime import timedelta

class Config:
    # Configuración de base de datos MariaDB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:koal@localhost:3307/synapse_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'tu-clave-secreta-muy-segura'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Configuración CORS
    CORS_ORIGINS = ['http://localhost:3000'] # Cambiar según el frontend
    
    # Configuración general
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'otra-clave-secreta'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}