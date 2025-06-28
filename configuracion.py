import os

class Configuracion:
    SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://SYSTEM:Pedro1718_@localhost:1521/XE'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'connect_args': {
            'encoding': 'UTF-8',
            'nencoding': 'UTF-8'
        }
    }
    SECRET_KEY = os.urandom(24)
    # configuracion para jwt
    JWT_SECRET_KEY = os.urandom(24)
    JWT_ACCESS_TOKEN_EXPIRES = False  # aqui los token no expiran
