from flask import render_template, request, redirect, url_for, flash, session
from . import acceso_bp
from models import Usuario, registrar_log # Importamos tus herramientas
from models import db, Usuario, Persona, Rol
from modulos.usuarios import usuarios_bp

@acceso_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form.get('usuario')
        password = request.form.get('password')

        user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

        if user and user.check_password(password):
            # Si todo bien, guardamos en la sesión de Flask
            session['user_id'] = user.id_usuario
            session['user_name'] = user.nombre_usuario
            session['user_rol'] = user.rol.nombre_rol
            
            registrar_log(user.id_usuario, "LOGIN_EXITOSO", descripcion="Acceso correcto al sistema")
            
            flash(f'Bienvenida de nuevo, {user.nombre_usuario}', 'success')
            return redirect(url_for('acceso.dashboard'))
        else:
            registrar_log(None, "LOGIN_FALLIDO", descripcion=f"Intento fallido con usuario: {nombre_usuario}")
            
            flash('Credenciales incorrectas', 'danger')
        
        session['user_id'] = user.id_usuario
        session['user_name'] = user.nombre_usuario
        session['user_rol'] = user.rol.nombre_rol # O como se llame en tu modelo

    return render_template('login.html')

@acceso_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', active_page='dashboard')

@usuarios_bp.route('/baja/<int:id>')
def baja_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.estatus = 'INACTIVO' # O el valor que uses para desactivar
    db.session.commit()
    flash('Usuario desactivado', 'warning')
    return redirect(url_for('usuarios.listado_usuarios'))

@acceso_bp.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('acceso.login'))