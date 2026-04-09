from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from . import usuarios_bp
from models import db, Usuario, Persona, Rol, registrar_log
from forms import BeautyUserForm 
from werkzeug.security import generate_password_hash

from modulos import usuarios

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def usuarios_form():
    if current_user.id_rol != 1:
        flash('No tienes permiso para crear usuarios.', 'danger')
        return redirect(url_for('acceso.dashboard'))
    
    form = BeautyUserForm()
    # Cargamos los roles disponibles
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]

    if form.validate_on_submit():
        try:
            # 1. Crear registro en Persona
            nueva_persona = Persona(
                nombre_persona=form.nombre.data,
                apellidos=form.apellidos.data,
                correo=form.email.data,
                telefono=form.telefono.data,
                direccion=request.form.get('direccion', Persona.direccion), # Si no se envía, se mantiene el valor actual (en este caso sería None)
                genero=request.form.get('genero', 'Sin especificar'),
                fecha_nacimiento=form.fecha_nacimiento.data
            )
            db.session.add(nueva_persona)
            db.session.flush() # Para obtener el id_persona antes del commit

            # 2. Crear registro en Usuario
            nuevo_usuario = Usuario(
                nombre_usuario=form.username.data,
                contrasenia=generate_password_hash(form.password.data),
                id_persona=nueva_persona.id_persona,
                id_rol=form.id_rol.data,
                estatus='ACTIVO'
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            rol_seleccionado = Rol.query.get(form.id_rol.data)
            if 'empleado' in rol_seleccionado.nombre_rol.lower():
                from models import Empleado
                nuevo_empleado = Empleado(
                    id_usuario=nuevo_usuario.id_usuario,
                    id_persona=nueva_persona.id_persona,
                    especialidad=form.especialidad.data if form.especialidad.data else "General"
                )
                db.session.add(nuevo_empleado)

            db.session.commit()
            
            registrar_log(
                usuario_id=current_user.id_usuario,
                accion="CREACION_USUARIO",
                modulo="Usuarios",
                detalle=f"Se creó el usuario: {nuevo_usuario.nombre_usuario}"
            )
            
            flash('¡Usuario creado con éxito!', 'success')
            return redirect(url_for('usuarios.listado_usuarios'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar en la base de datos: {str(e)}', 'danger')

    return render_template('usuarios/form.html', form=form, editando=False)


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    persona = Persona.query.get_or_404(usuario.id_persona)

    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('acceso.dashboard'))
    
    form = BeautyUserForm()
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]

    # Carga inicial de datos
    if request.method == 'GET':
        form.nombre.data = persona.nombre_persona
        form.apellidos.data = persona.apellidos
        form.email.data = persona.correo
        form.telefono.data = persona.telefono
        form.username.data = usuario.nombre_usuario
        form.id_rol.data = usuario.id_rol
        form.fecha_nacimiento.data = persona.fecha_nacimiento
        # La especialidad se busca si es empleado
        from models import Empleado
        emp = Empleado.query.filter_by(id_usuario=usuario.id_usuario).first()
        if emp:
            form.especialidad.data = emp.especialidad

    if form.validate_on_submit():
        try:
            # 1. Actualizar Persona
            persona.nombre_persona = form.nombre.data
            persona.apellidos = form.apellidos.data
            persona.correo = form.email.data
            persona.telefono = form.telefono.data
            persona.fecha_nacimiento = form.fecha_nacimiento.data
            persona.direccion = request.form.get('direccion', persona.direccion)
            persona.genero = request.form.get('genero', persona.genero)
            
            # 2. Actualizar Usuario
            usuario.nombre_usuario = form.username.data
            usuario.id_rol = form.id_rol.data
            
            if form.password.data: # Solo si escribió una nueva
                usuario.contrasenia = generate_password_hash(form.password.data)

            # 3. Actualizar o Crear registro de Empleado
            rol_seleccionado = Rol.query.get(form.id_rol.data)
            from models import Empleado
            empleado_existente = Empleado.query.filter_by(id_usuario=usuario.id_usuario).first()

            if 'empleado' in rol_seleccionado.nombre_rol.lower():
                if empleado_existente:
                    empleado_existente.especialidad = form.especialidad.data
                else:
                    nuevo_emp = Empleado(
                        id_usuario=usuario.id_usuario,
                        id_persona=persona.id_persona,
                        especialidad=form.especialidad.data
                    )
                    db.session.add(nuevo_emp)
            elif empleado_existente:
                # Si ya no es empleado, podrías decidir borrarlo o dejarlo
                pass
            
            db.session.commit()
            
            registrar_log(
                usuario_id=current_user.id_usuario,
                accion="EDICION_USUARIO",
                modulo="Usuarios",
                detalle=f"Se actualizó al usuario: {usuario.nombre_usuario}"
            )
            
            flash(f'El usuario {usuario.nombre_usuario} ha sido actualizado.', 'success')
            return redirect(url_for('usuarios.listado_usuarios')) 
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    return render_template('usuarios/form.html', form=form, editando=True, persona=persona)

@usuarios_bp.route('/listado')
@login_required
def listado_usuarios():
    search = request.args.get('search', '')
    rol_filter = request.args.get('rol', '')
    estado_filter = request.args.get('estado', '')

    query = db.session.query(Usuario, Persona).join(Persona, Usuario.id_persona == Persona.id_persona)

    if search:
        search_term = search.strip()
        
        full_name_db = db.func.concat(Persona.nombre_persona, ' ', Persona.apellidos)
        
        query = query.filter(
            (full_name_db.ilike(f'%{search_term}%')) | 
            (Persona.nombre_persona.ilike(f'%{search_term}%')) | 
            (Persona.apellidos.ilike(f'%{search_term}%')) |
            (Persona.correo.ilike(f'%{search_term}%'))
        )
    if rol_filter:
        query = query.join(Rol, Usuario.id_rol == Rol.id_rol).filter(Rol.nombre_rol == rol_filter)
    
    if estado_filter:
        query = query.filter(Usuario.estatus == estado_filter)

    usuarios = query.all() 

    return render_template('usuarios/listado.html', usuarios=usuarios, active_page='usuarios')

@usuarios_bp.route('/desactivar/<int:id>', methods=['GET']) # Cambiado a usuarios_bp
@login_required
def confirmar_desactivacion(id):
    info = db.session.query(Usuario, Persona).join(Persona).filter(Usuario.id_usuario == id).first_or_404()
    return render_template('usuarios/eliminar_usuario.html', info=info)

@usuarios_bp.route('/eliminar_logico/<int:id>', methods=['POST']) # Nombre que busca tu HTML
@login_required
def eliminar_logico(id):
    if current_user.id_rol != 1:
        return redirect(url_for('acceso.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)

    if usuario.id_usuario == current_user.id_usuario:
        flash("No puedes desactivar tu propia cuenta.", "warning")
        return redirect(url_for('usuarios.listado_usuarios'))
    
    usuario.estatus = 'INACTIVO'
    
    try:
        db.session.commit()
        
        registrar_log(
            usuario_id=current_user.id_usuario,
            accion="BAJA_USUARIO",
            tabla="usuario",
            registro_id=usuario.id_usuario,
            descripcion=f"Se desactivó al usuario: {usuario.nombre_usuario} (Cambio a INACTIVO)"
        )
        
        flash(f'El usuario {usuario.nombre_usuario} ha sido desactivado.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la baja: {str(e)}', 'danger')
        
    return redirect(url_for('usuarios.listado_usuarios'))

@usuarios_bp.route('/perfil')
@login_required
def ver_perfil():
    user_id = session.get('user_id')
    info = db.session.query(Usuario, Persona).join(Persona).filter(Usuario.id_usuario == user_id).first()
    
    return render_template('usuarios/peerfil.html', info=info)

@usuarios_bp.route('/ver/<int:id>')
@login_required
def ver_perfil_especifico(id):
    info = db.session.query(Usuario, Persona).join(Persona).filter(Usuario.id_usuario == id).first_or_404()
    
    return render_template('usuarios/perfil.html', info=info, solo_lectura=True)