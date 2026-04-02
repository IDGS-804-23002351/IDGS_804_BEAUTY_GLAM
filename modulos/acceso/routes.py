from flask import render_template, request, redirect, url_for, flash, session
from . import acceso_bp
from models import Usuario, registrar_log # Importamos tus herramientas
from models import db, Usuario, Persona, Rol
from modulos.usuarios import usuarios_bp

@acceso_bp.route('/inicio', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form.get('usuario')
        password = request.form.get('password')

        user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

        if user and user.check_password(password):
            # CORRECCIÓN: Usar 'user' (la instancia), no 'Usuario' (la clase)
            if user.estatus == 'INACTIVO':
                registrar_log(
                    usuario_id=user.id_usuario,
                    accion="LOGIN_BLOQUEADO",
                    modulo="Acceso",
                    detalle=f"Intento de ingreso con cuenta desactivada: {nombre_usuario}"
                )
                flash('Tu cuenta ha sido desactivada.', 'danger')
                return redirect(url_for('acceso.login'))

            # Si todo bien, guardamos en la sesión
            session['user_id'] = user.id_usuario
            session['user_name'] = user.nombre_usuario
            session['user_rol'] = user.rol.nombre_rol
            
            registrar_log(
                usuario_id=user.id_usuario,
                accion="LOGIN_EXITOSO",
                modulo="Acceso",
                detalle="Acceso correcto"
            )
            flash(f'Bienvenida de nuevo, {user.nombre_usuario}', 'success')
            return redirect(url_for('acceso.dashboard'))
        
        else:
            # Caso de credenciales incorrectas
            registrar_log(usuario_id=0, accion="LOGIN_FALLIDO", modulo="Acceso", detalle=f"Usuario: {nombre_usuario}")
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('acceso.login'))

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
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    registrar_log(
    usuario_id=user_id,
    accion="LOGOUT",
    modulo="Acceso",  
    detalle=f"Sesión cerrada" 
    )
    
    session.clear() 
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('acceso.login')) 