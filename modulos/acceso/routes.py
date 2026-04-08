import random
import string
from flask import render_template, request, redirect, url_for, flash, session
from . import acceso_bp
from models import Cliente, Usuario, registrar_log 
from models import db, Usuario, Persona, Rol, Cita, Producto, Pago
from modulos.usuarios import usuarios_bp
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message, Mail
from werkzeug.security import generate_password_hash, check_password_hash

mail = Mail()

@acceso_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('acceso.dashboard'))
    
    if request.method == 'POST':
        nombre_usuario = request.form.get('usuario')
        password = request.form.get('password')
        user_captcha = request.form.get('captcha_ans')

        try:
            total_esperado = int(session.get('captcha_n1', 0)) + int(session.get('captcha_n2', 0))
            if int(user_captcha) != total_esperado:
                flash('Captcha incorrecto. Intenta de nuevo.', 'danger')
                return redirect(url_for('acceso.login'))
        except (ValueError, TypeError):
            flash('Error en la validación humana.', 'danger')
            return redirect(url_for('acceso.login'))

        user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

        if user and user.check_password(password):
            if user.estatus == 'INACTIVO':
                flash('Tu cuenta ha sido desactivada por administración.', 'danger')
                return redirect(url_for('acceso.login'))
            
            if user.rol and user.rol.estatus == 'INACTIVO':
                flash('El acceso para tu tipo de usuario está deshabilitado temporalmente.', 'danger')
                registrar_log(usuario_id=user.id_usuario, accion="LOGIN_BLOQUEADO", modulo="Acceso", detalle="Intento de entrada con Rol Inactivo")
                return redirect(url_for('acceso.login'))

            login_user(user)
            session['user_id'] = user.id_usuario
            session['user_name'] = user.nombre_usuario
            session['user_rol'] = user.rol.nombre_rol

            registrar_log(usuario_id=user.id_usuario, accion="LOGIN_EXITOSO", modulo="Acceso", detalle="Acceso correcto")
            flash(f"¡Hola de nuevo, {user.nombre_usuario}!", "success")
            return redirect(url_for('acceso.dashboard'))
        
        else:
            registrar_log(usuario_id=0, accion="LOGIN_FALLIDO", modulo="Acceso", detalle=f"Usuario: {nombre_usuario}")
            flash('Credenciales incorrectas.', 'danger')
            return redirect(url_for('acceso.login'))

    session['captcha_n1'] = random.randint(1, 10)
    session['captcha_n2'] = random.randint(1, 10)
    
    return render_template('login.html')

@acceso_bp.route('/dashboard')
@login_required
def dashboard():
    resumen = {}
    hoy = datetime.now().date()

    persona = Persona.query.get(current_user.id_persona)
    
    if current_user.id_rol == 1:
        resumen['total_usuarios'] = Usuario.query.count()
        resumen['citas_dia'] = Cita.query.filter(db.func.date(Cita.fecha_hora) == hoy).count()
        resumen['total_usuarios'] = Usuario.query.count()
        resumen['citas_dia'] = Cita.query.filter(db.func.date(Cita.fecha_hora) == hoy).count()
        resumen['stock_bajo'] = Producto.query.filter(Producto.stock_actual <= 5).count()
        
        total_pago = db.session.query(db.func.sum(Pago.total)).filter(db.func.date(Pago.fecha_pago) == hoy).scalar()
        resumen['ventas'] = f"${total_pago if total_pago else 0:,.2f}"
        
    elif current_user.id_rol == 2:
        resumen['mis_citas_count'] = Cita.query.filter(Cita.id_empleado == current_user.id_persona, db.func.date(Cita.fecha_hora) == hoy).count()
        
    elif current_user.id_rol == 3:
        prox_cita = Cita.query.filter(Cita.id_cliente == current_user.id_persona, Cita.fecha_hora >= datetime.now()).first()
        resumen['mi_proxima_cita'] = prox_cita.fecha_hora.strftime('%d/%m %H:%M') if prox_cita else "Sin citas"

    elif current_user.id_rol == 4:
        resumen['mis_productos'] = Producto.query.count()

    return render_template('dashboard.html', active_page='dashboard', resumen=resumen, persona=persona)

@usuarios_bp.route('/baja/<int:id>')
@login_required
def baja_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.estatus = 'INACTIVO' 
    db.session.commit()
    flash('Usuario desactivado', 'warning')
    return redirect(url_for('usuarios.listado_usuarios'))


@acceso_bp.route('/logout')
@login_required
def logout():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    registrar_log(
    usuario_id=user_id,
    accion="LOGOUT",
    modulo="Acceso",  
    detalle=f"Usuario {user_name} cerró sesión"
    )
    
    logout_user()
    session.clear() 
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('acceso.login')) 

@acceso_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        existe = Persona.query.filter_by(correo=correo).first()
        if existe:
            flash('Este correo ya está registrado en Beauty & Glam.', 'warning')
            return redirect(url_for('acceso.registro'))

        try:
            nueva_persona = Persona(
                nombre_persona=nombre, 
                apellidos=apellidos, 
                correo=correo
            )
            db.session.add(nueva_persona)
            db.session.flush() 

            nuevo_usuario = Usuario(
                nombre_usuario=correo.split('@')[0], 
                contrasenia=generate_password_hash(password), 
                id_persona=nueva_persona.id_persona,
                id_rol=3, 
                estatus='ACTIVO'
            )
            db.session.add(nuevo_usuario)
            db.session.flush() # Esto genera el id_usuario

            nuevo_cliente = Cliente(
                id_persona=nueva_persona.id_persona,
                id_usuario=nuevo_usuario.id_usuario,
                estatus='ACTIVO'
            )
            db.session.add(nuevo_cliente)

            db.session.commit()

            registrar_log(usuario_id=nuevo_usuario.id_usuario, accion="REGISTRO", modulo="Acceso", detalle="Nuevo cliente creado exitosamente")
            
            flash(f'¡Cuenta creada con éxito! Tu nombre de usuario para ingresar es: {nuevo_usuario.nombre_usuario}', 'success')
            return redirect(url_for('acceso.login'))

        except Exception as e:
            db.session.rollback()
            print(f"Error en el servidor: {e}") # Para que lo veas en tu terminal
            flash(f'Error al registrar: {str(e)}', 'danger')

    return render_template('registro.html')

@acceso_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'POST':
        email = request.form.get('correo')
        persona = Persona.query.filter_by(correo=email).first()
        
        if persona:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            session['reset_code'] = codigo
            session['reset_email'] = email
            
            msg = Message("Recupera tu acceso - Beauty & Glam",
                          sender="soporte@beautyglam.com",
                          recipients=[email])
            msg.html = render_template('emails/recuperacion_email.html', codigo=codigo, nombre=persona.nombre_persona)
            mail.send(msg)

            flash('Hemos enviado un código a tu correo.', 'info')
            return redirect(url_for('acceso.verificar_codigo')) 
        
        else:
            flash('El correo no se encuentra en el sistema.', 'danger')
        return redirect(url_for('acceso.recuperar_password')) 
    
    return render_template('recuperar_pass.html')

@acceso_bp.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo')
        codigo_real = session.get('reset_code')

        if codigo_ingresado == codigo_real:
            flash('Código verificado. Ahora puedes cambiar tu contraseña.', 'success')
            return redirect(url_for('acceso.restablecer_password'))
        
        flash('El código es incorrecto. Intenta de nuevo.', 'danger')
    
    return render_template('verificar_codigo.html')

@acceso_bp.route('/restablecer-password', methods=['GET', 'POST'])
def restablecer_password():
    if 'reset_email' not in session:
        return redirect(url_for('acceso.recuperar_password'))

    if request.method == 'POST':
        nueva_pass = request.form.get('password')
        confirmar_pass = request.form.get('confirm_password')
        email = session.get('reset_email')

        if nueva_pass != confirmar_pass:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('acceso.restablecer_password'))

        # Actualizamos en la tabla Usuario
        persona = Persona.query.filter_by(correo=email).first()
        if persona:
            usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
            usuario.contrasenia = generate_password_hash(nueva_pass)
            db.session.commit()
            
            # Limpiamos sesión de recuperación
            session.pop('reset_code', None)
            session.pop('reset_email', None)

            flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('acceso.login'))

    return render_template('restablecer_pass.html')