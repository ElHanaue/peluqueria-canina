import os
from datetime import timedelta, datetime
from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from modelos import Veterinario, db, Cliente, Mascota, Cita
from formularios import FormularioRegistroCliente, FormularioRegistroMascota, FormularioCita
from configuracion import Configuracion
from sqlalchemy import inspect, text
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, 
    get_jwt_identity, set_access_cookies, unset_jwt_cookies
)
#flask es una app web dirigida a python
#configura la ubicación de los archivos y plantillas para la aplicación Flask
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'plantillas')

app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Configuracion)

# Configuración JWT (una medida de seguridad q resguarda datos y procesos de la app ademas de autentificar y autorizar.)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
jwt = JWTManager(app)

# Inicia la base de datos
with app.app_context():
    try:
        connection = db.engine.connect()
        connection.close()
        db.create_all()
        
        # Verificar estructura de las tablas
        inspector = inspect(db.engine)
        if 'CITAS' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('CITAS')]
            if 'completada' not in columns:
                print("⚠ Advertencia: La columna 'completada' no existe en CITAS")
    except Exception as e:
        print(f"Error durante la inicialización: {str(e)}")

# Rutas principales ( coloquialmente hablando son las conexiones directa a las plantillas)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        contrasena = request.form.get('contrasena', '').strip()
        
        cliente = Cliente.query.filter_by(correo=correo).first()
        
        if cliente and check_password_hash(cliente.contrasena, contrasena):
            token = create_access_token(identity=str(cliente.id))
            response = make_response(redirect(url_for('perfil', cliente_id=cliente.id)))
            set_access_cookies(response, token)
            flash('Inicio de sesión exitoso', 'success')
            return response
        
        flash('Credenciales inválidas', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    flash('Sesión cerrada', 'info')
    return response

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = FormularioRegistroCliente()
    if formulario.validate_on_submit():
        try:
            nuevo_cliente = Cliente(
                nombre=formulario.nombre.data.strip(),
                correo=formulario.correo.data.lower().strip(),
                contrasena=generate_password_hash(formulario.contrasena.data)
            )
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            token = create_access_token(identity=str(nuevo_cliente.id))
            response = make_response(redirect(url_for('perfil', cliente_id=nuevo_cliente.id)))
            set_access_cookies(response, token)
            flash('Registro exitoso', 'success')
            return response
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar', 'error')
    return render_template('registrar_cliente.html', formulario=formulario)

@app.route('/perfil/<int:cliente_id>', methods=['GET', 'POST'])
@jwt_required()
def perfil(cliente_id):
    try:
        current_user = int(get_jwt_identity())
        if current_user != cliente_id:
            flash('No autorizado', 'error')
            return redirect(url_for('index'))
        
        cliente = Cliente.query.get_or_404(cliente_id)
        formulario_mascota = FormularioRegistroMascota()
        mascotas = Mascota.query.filter_by(cliente_id=cliente_id).all()
        citas = Cita.query.filter_by(cliente_id=cliente_id).order_by(Cita.fecha).all()
        
        if request.method == 'POST' and formulario_mascota.validate_on_submit():
            try:
                nueva_mascota = Mascota(
                    nombre=formulario_mascota.nombre.data.strip(),
                    raza=formulario_mascota.raza.data.strip(),
                    peso=float(formulario_mascota.peso.data),
                    edad=int(formulario_mascota.edad.data),
                    cliente_id=cliente_id
                )
                db.session.add(nueva_mascota)
                db.session.commit()
                flash('Mascota registrada', 'success')
                return redirect(url_for('perfil', cliente_id=cliente_id))
            except Exception as e:
                db.session.rollback()
                flash('Error al registrar mascota', 'error')
        
        return render_template(
            'perfil.html',
            cliente=cliente,
            formulario=formulario_mascota,
            mascotas=mascotas,
            citas=citas
        )
    except Exception as e:
        flash('Error al cargar perfil', 'error')
        return redirect(url_for('index'))

@app.route('/solicitar_cita', methods=['GET', 'POST'])
@jwt_required()
def solicitar_cita():
    try:
        cliente_id = int(get_jwt_identity())
        cliente = Cliente.query.get_or_404(cliente_id)
        formulario = FormularioCita()
        
        # Obtener mascotas del cliente
        mascotas = Mascota.query.filter_by(cliente_id=cliente_id).all()
        if not mascotas:
            flash('Debe registrar al menos una mascota antes de agendar una cita', 'error')
            return redirect(url_for('perfil', cliente_id=cliente_id))
        
        # Configurar opciones del formulario
        formulario.mascota_id.choices = [(m.id, f"{m.nombre} ({m.raza})") for m in mascotas]
        
        if formulario.validate_on_submit():
            try:
                # Verificar mascota
                mascota = next((m for m in mascotas if m.id == formulario.mascota_id.data), None)
                if not mascota:
                    raise ValueError("La mascota seleccionada no pertenece al cliente")
                
                # Asignar veterinario 
                veterinario = Veterinario.query.first()  # Toma el primer veterinario
                
                if not veterinario:
                    flash('No hay veterinarios disponibles. Por favor contacte al administrador.', 'error')
                    return redirect(url_for('solicitar_cita'))
                
                # Crear cita
                nueva_cita = Cita(
                    fecha=formulario.fecha.data,
                    mascota_id=formulario.mascota_id.data,
                    cliente_id=cliente_id,
                    veterinario_id=veterinario.id,
                    completada=False
                )
                
                db.session.add(nueva_cita)
                db.session.commit()
                
                flash('¡Cita agendada correctamente!', 'success')
                return redirect(url_for('perfil', cliente_id=cliente_id))
            
            except ValueError as e:
                db.session.rollback()
                flash(str(e), 'error')
            except Exception as e:
                db.session.rollback()
                print(f"Error al agendar cita: {str(e)}")
                flash('Error al procesar la solicitud. Intente nuevamente.', 'error')
        
        return render_template('solicitar_cita.html', 
                            formulario=formulario, 
                            cliente=cliente,
                            ahora=datetime.now())
    
    except Exception as e:
        print(f"Error en solicitar_cita: {str(e)}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('perfil', cliente_id=cliente_id))

if __name__ == '__main__':
    app.run(debug=True)
