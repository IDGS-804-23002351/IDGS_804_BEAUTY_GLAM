from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db, Usuario, Persona, registrar_log 
from . import perfil_bp
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

@perfil_bp.route('/perfil')
@login_required
def ver_perfil():
    usuario = Usuario.query.get(current_user.id_usuario)
    return render_template('vistaClientes/perfil/perfil.html', usuario=usuario, persona=usuario.persona)

@perfil_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    usuario = Usuario.query.get(current_user.id_usuario)
    persona = usuario.persona

    ahora = datetime.now()
    if persona.ultima_actualizacion:
        tiempo_permitido = persona.ultima_actualizacion + timedelta(hours=24)
        if ahora < tiempo_permitido:
            tiempo_restante = tiempo_permitido - ahora
            horas = int(tiempo_restante.total_seconds() // 3600)
            minutos = int((tiempo_restante.total_seconds() % 3600) // 60)
            flash(f"Solo puedes editar tu perfil una vez cada 24 horas. Faltan {horas}h {minutos}m.", "warning")
            return redirect(url_for('perfil.ver_perfil'))

    nuevo_username = request.form.get('nombre_usuario', '').strip()
    nuevo_correo = request.form.get('correo', '').strip()
    nombre_completo = request.form.get('nombre_completo', '').strip()
    
    try:
        if nuevo_username and nuevo_username != usuario.nombre_usuario:
            if Usuario.query.filter_by(nombre_usuario=nuevo_username).first():
                flash("Ese nombre de usuario ya está ocupado por otra persona.", "danger")
                return redirect(url_for('perfil.ver_perfil'))
            usuario.nombre_usuario = nuevo_username

        if nombre_completo:
            partes = nombre_completo.split(' ', 1)
            persona.nombre_persona = partes[0]
            persona.apellidos = partes[1] if len(partes) > 1 else ""
        
        persona.telefono = request.form.get('telefono', '').strip()
        persona.correo = nuevo_correo
        persona.genero = request.form.get('genero')
        
        f_nac = request.form.get('fecha_nacimiento')
        if f_nac:
            persona.fecha_nacimiento = datetime.strptime(f_nac, '%Y-%m-%d').date()

        persona.ultima_actualizacion = ahora
        db.session.commit()

        session['_user_id'] = usuario.id_usuario 
        
        registrar_log(usuario.id_usuario, "ACTUALIZAR_PERFIL", modulo="Perfil", detalle=f"Username cambiado a: {nuevo_username}")
        flash("¡Perfil actualizado con éxito!", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Ocurrió un error inesperado: {str(e)}", "danger")

    return redirect(url_for('perfil.ver_perfil'))