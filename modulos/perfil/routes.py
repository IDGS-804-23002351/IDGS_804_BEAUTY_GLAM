from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Usuario, Persona, registrar_log 
from . import perfil_bp
from werkzeug.security import generate_password_hash, check_password_hash

@perfil_bp.route('/perfil')
@login_required
def ver_perfil():
    return render_template('vistaClientes/perfil/perfil.html')

@perfil_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    usuario = Usuario.query.get(current_user.id_usuario)
    persona = usuario.persona

    # --- LÓGICA DE LÍMITE (24 HORAS) ---
    if persona.ultima_actualizacion:
        tiempo_limite = persona.ultima_actualizacion + timedelta(hours=24)
        if datetime.now() < tiempo_limite:
            flash("Solo puedes editar tu perfil una vez cada 24 horas.", "warning")
            return redirect(url_for('perfil.ver_perfil'))

    # Leer datos del form
    nuevo_username = request.form.get('nombre_usuario', '').strip()
    nuevo_correo = request.form.get('correo', '').strip()
    nombre_completo = request.form.get('nombre_completo', '').strip()
    
    try:
        # Validar Nombre de Usuario único
        if nuevo_username != usuario.nombre_usuario:
            if Usuario.query.filter_by(nombre_usuario=nuevo_username).first():
                flash("Ese nombre de usuario ya existe.", "danger")
                return redirect(url_for('perfil.ver_perfil'))
            usuario.nombre_usuario = nuevo_username

        # Actualizar Persona
        partes = nombre_completo.split(' ', 1)
        persona.nombre_persona = partes[0]
        persona.apellidos = partes[1] if len(partes) > 1 else ""
        persona.telefono = request.form.get('telefono')
        persona.correo = nuevo_correo
        persona.genero = request.form.get('genero')
        
        f_nac = request.form.get('fecha_nacimiento')
        if f_nac:
            persona.fecha_nacimiento = datetime.strptime(f_nac, '%Y-%m-%d').date()

        # Marca de tiempo
        persona.ultima_actualizacion = datetime.now()
        
        db.session.commit()
        registrar_log(usuario.id_usuario, "ACTUALIZAR_PERFIL", modulo="Perfil", detalle="Datos y username actualizados")
        flash("Perfil actualizado con éxito.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for('perfil.ver_perfil'))