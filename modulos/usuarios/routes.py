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
            
            id_admin = session.get('user_id') or 0
            registrar_log(
                id_admin, 
                "CREACION_USUARIO", 
                descripcion=f"Se creó al usuario {form.username.data} con éxito."
            )
            
            flash('¡Usuario creado con éxito!', 'success')
            return redirect(url_for('usuarios.listado_usuarios'))
            
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
        
        # Si el usuario escribió una nueva contraseña, la actualizamos
        if form.password.data:
            usuario.contrasenia = generate_password_hash(form.password.data)
            
        db.session.commit()
        flash('¡Usuario actualizado!', 'success')
        return redirect(url_for('usuarios.listado_usuarios'))                       

    return render_template('usuarios/form.html', form=form, editando=True)