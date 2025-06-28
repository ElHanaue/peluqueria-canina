from flask_wtf import FlaskForm
from wtforms import DateTimeField, FloatField, SelectField, StringField, PasswordField, SubmitField, IntegerField 
FloatField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from datetime import datetime

class FormularioRegistroCliente(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    correo = StringField('Correo', validators=[DataRequired(), Email(), Length(max=100)])
    contrasena = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrarse')

class FormularioRegistroMascota(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    raza = StringField('Raza', validators=[DataRequired(), Length(max=100)])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    edad = IntegerField('Edad (años)', validators=[DataRequired()])
    submit = SubmitField('Registrar Mascota')

class FormularioCita(FlaskForm):
    fecha = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', 
                         validators=[DataRequired()])
    mascota_id = SelectField('Mascota', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agendar Cita')
