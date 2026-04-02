from flask import render_template, request, redirect, url_for, flash, session
from . import usuarios_bp
from models import db, Usuario, Persona, Rol, registrar_log
from forms import BeautyUserForm 
from werkzeug.security import generate_password_hash

from modulos import usuarios

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
def usuarios_form():
    form = BeautyUserForm()
    
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]

    if form.validate_on_submit():
        nueva_persona = Persona(
            nombre_persona=form.nombre.data,
            apellidos=form.apellidos.data,
            correo=form.email.data,
            telefono=form.telefono.data
        )
        db.session.add(nueva_persona)
        db.session.flush() 

        password_enc = generate_password_hash(form.password.data)
        nuevo_usuario = Usuario(
            nombre_usuario=form.username.data,
            contrasenia=password_enc,
            id_persona=nueva_persona.id_persona,
            id_rol=form.id_rol.data
        )
        db.session.add(nuevo_usuario)
        
        try:
            db.session.commit()
            
            # Registro en MongoDB
            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="EDICION_USUARIO",
                tabla="usuario/persona",
                registro_id=Usuario.id_usuario,
                descripcion=f"Se actualizaron los datos del usuario: {Usuario.nombre_usuario}"
            )
            
            flash('¡Usuario actualizado!', 'success')
            return redirect(url_for('usuarios.listado_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')

    return render_template('usuarios/form.html', form=form)

@usuarios_bp.route('/listado')
def listado_usuarios():
    usuarios = db.session.query(Usuario, Persona).join(Persona, Usuario.id_persona == Persona.id_persona).all()
    return render_template('usuarios/listado.html', usuarios=usuarios, active_page='usuarios')

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    persona = Persona.query.get_or_404(usuario.id_persona)
    
    form = BeautyUserForm()
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]

    if request.method == 'GET':
        form.nombre.data = persona.nombre_persona
        form.apellidos.data = persona.apellidos
        form.email.data = persona.correo
        form.telefono.data = persona.telefono
        
        form.username.data = usuario.nombre_usuario
        form.id_rol.data = usuario.id_rol

    if form.validate_on_submit():
        persona.nombre_persona = form.nombre.data
        persona.apellidos = form.apellidos.data
        persona.correo = form.email.data
        persona.telefono = form.telefono.data
        
        usuario.nombre_usuario = form.username.data
        usuario.id_rol = form.id_rol.data
        
        if form.password.data:
            usuario.contrasenia = generate_password_hash(form.password.data)      
    try:
        db.session.commit()
        
        # Registramos el movimiento crítico en Mongo
        registrar_log(
            usuario_id=session.get('user_id', 0),
            accion="EDICION_USUARIO",
            tabla="usuario",
            registro_id=usuario.id_usuario,
            descripcion=f"Se actualizó la información del usuario: {usuario.nombre_usuario}"
        )
        
        flash(f'El usuario {usuario.nombre_usuario} ha sido actualizado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'danger')
        return redirect(url_for('usuarios.listado_usuarios'))                       

    return render_template('usuarios/form.html', form=form, editando=True)

@usuarios_bp.route('/eliminar/<int:id>')
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    usuario.estatus = 'INACTIVO'
    
    try:
        db.session.commit()
        
        registrar_log(
            usuario_id=session.get('user_id', 0),
            accion="BAJA_USUARIO",
            tabla="usuario",
            registro_id=usuario.id_usuario,
            descripcion=f"Se desactivó al usuario: {usuario.nombre_usuario} (Cambio a INACTIVO)"
        )
        
        flash(f'El usuario {usuario.nombre_usuario} ha sido desactivado con éxito.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la baja: {str(e)}', 'danger')
        
    return redirect(url_for('usuarios.listado_usuarios'))

@usuarios_bp.route('/perfil')
def ver_perfil():
    user_id = session.get('user_id')
    info = db.session.query(Usuario, Persona).join(Persona).filter(Usuario.id_usuario == user_id).first()
    
    return render_template('usuarios/perfil.html', info=info)