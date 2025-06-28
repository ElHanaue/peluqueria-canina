from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'CLIENTES'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    mascotas = db.relationship('Mascota', backref='propietario', lazy=True)
    citas = db.relationship('Cita', backref='cliente_rel', lazy=True)

class Mascota(db.Model):
    __tablename__ = 'MASCOTAS'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    raza = db.Column(db.String(100), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('CLIENTES.id'), nullable=False)
    citas = db.relationship('Cita', backref='mascota_rel', lazy=True)

class Veterinario(db.Model):
    __tablename__ = 'VETERINARIOS'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    citas = db.relationship('Cita', backref='veterinario_asignado', lazy=True)

class Cita(db.Model):
    __tablename__ = 'CITAS'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('MASCOTAS.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('CLIENTES.id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('VETERINARIOS.id'), nullable=True)
    completada = db.Column(db.Boolean, default=False)
    
    mascota = db.relationship('Mascota', backref='citas_asociadas')
    cliente = db.relationship('Cliente', backref='citas_cliente')
    veterinario = db.relationship('Veterinario', backref='citas_veterinario')
