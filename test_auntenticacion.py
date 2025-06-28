from flask.testing import FlaskClient
import pytest
from app import app, db
from modelos import Cliente
from werkzeug.security import generate_password_hash

@pytest.fixture
def cliente_test():
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False  
    })
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            test_user = Cliente(
                nombre="Usuario Test",
                correo="test@example.com",
                contrasena=generate_password_hash("password123")
            )
            db.session.add(test_user)
            db.session.commit()
        
        yield client
        
        with app.app_context():
            db.drop_all()

def test_login_exitoso(cliente_test: FlaskClient):
    """Prueba que el login redirige correctamente al perfil"""
    response = cliente_test.post('/login', data={
        'correo': 'test@example.com',
        'contrasena': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    assert b'perfil' in response.data.lower()
    assert b'logout' in response.data.lower()  

def test_login_fallido(cliente_test: FlaskClient):
    """Prueba que login falla con credenciales incorrectas"""
    response = cliente_test.post('/login', data={
        'correo': 'test@example.com',
        'contrasena': 'contrasena_incorrecta'
    })
    
    assert response.status_code == 200
    
    assert b'alert' in response.data.lower() or b'error' in response.data.lower()
    assert b'login' in response.data.lower()  

def test_registro_usuario(cliente_test: FlaskClient):
    """Prueba el registro de nuevos usuarios"""
    response = cliente_test.post('/registrar', data={
        'nombre': 'Nuevo Usuario',
        'correo': 'nuevo@example.com',
        'contrasena': 'micontraseña',
        'confirmar_contrasena': 'micontraseña'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    assert b'perfil' in response.data.lower()
    
    assert b'Nuevo Usuario' in response.data
