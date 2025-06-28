from flask_sqlalchemy import SQLAlchemy
import pytest
from datetime import datetime, timedelta
from app import app, db
from modelos import Cliente, Mascota, Cita, Veterinario

@pytest.fixture
def contexto_bd():
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_creacion_cliente(contexto_bd: SQLAlchemy):
    """Prueba la creación de clientes en la base de datos"""
    cliente = Cliente(
        nombre="Cliente Test",
        correo="cliente@test.com",
        contrasena="hashed_password"
    )
    contexto_bd.session.add(cliente)
    contexto_bd.session.commit()
    
    assert cliente.id is not None
    assert Cliente.query.count() == 1

def test_relacion_cliente_mascota(contexto_bd: SQLAlchemy):
    """Prueba la relación entre clientes y mascotas"""
    cliente = Cliente(nombre="Dueño", correo="dueno@test.com", contrasena="123")
    mascota = Mascota(
        nombre="Mascota Test",
        raza="Labrador",
        peso=15.5,
        edad=3,
        cliente=cliente  # Usando la relación backref
    )
    contexto_bd.session.add_all([cliente, mascota])
    contexto_bd.session.commit()
    
    assert len(cliente.mascotas) == 1
    assert cliente.mascotas[0].nombre == "Mascota Test"

def test_creacion_cita(contexto_bd: SQLAlchemy):
    """Prueba el agendamiento de citas"""
    cliente = Cliente(nombre="Cliente Cita", correo="cita@test.com", contrasena="123")
    veterinario = Veterinario(nombre="Dr. Veterinario")
    mascota = Mascota(nombre="Perro Cita", cliente=cliente)
    
    cita = Cita(
        fecha=datetime.now() + timedelta(days=1),
        mascota=mascota,
        cliente=cliente,
        veterinario=veterinario,
        completada=False
    )
    
    contexto_bd.session.add_all([cliente, veterinario, mascota, cita])
    contexto_bd.session.commit()
    
    assert len(cliente.citas) == 1
    assert cliente.citas[0].mascota.nombre == "Perro Cita"
