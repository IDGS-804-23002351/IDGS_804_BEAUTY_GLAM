from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Usuario, Persona, registrar_log # Importamos tu función de bitacora
from . import perfil_bp
from werkzeug.security import generate_password_hash, check_password_hash

@perfil_bp.route('/perfil')
@login_required
def ver_perfil():
    return render_template('vistaClientes/perfil/perfil.html') # Asegúrate que la ruta del html sea correcta

@perfil_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    nombre_completo = request.form.get('nombre_completo', '').strip()
    nuevo_telefono = request.form.get('telefono')
    nuevo_correo = request.form.get('correo')
    
    partes = nombre_completo.split(' ', 1)
    nombre = partes[0]
    apellidos = partes[1] if len(partes) > 1 else ""

    pass_actual = request.form.get('pass_actual')
    pass_nueva = request.form.get('pass_nueva')

    usuario = Usuario.query.get(current_user.id_usuario)
    persona = usuario.persona

    try:
        persona.nombre_persona = nombre
        persona.apellidos = apellidos
        persona.telefono = nuevo_telefono
        persona.correo = nuevo_correo

        if pass_actual and pass_nueva:
            if check_password_hash(usuario.contrasenia, pass_actual):
                usuario.set_password(pass_nueva)
                registrar_log(usuario.id_usuario, 
                              "CAMBIO_CONTRASEÑA", 
                              modulo="Perfil", 
                              detalle="El usuario cambió su contraseña")
            else:
                flash("La contraseña actual es incorrecta", "danger")
                return redirect(url_for('perfil.ver_perfil'))

        db.session.commit()
        
        registrar_log(
            usuario_id=usuario.id_usuario,
            accion="ACTUALIZAR_PERFIL",
            modulo="Perfil",
            detalle=f"Actualización de datos personales para {usuario.nombre_usuario}"
        )

        flash("Perfil actualizado con éxito", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")

    return redirect(url_for('perfil.ver_perfil'))