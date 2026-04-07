from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from . import roles_bp
from models import db, Rol, Permisos, registrar_log, Modulo, RolPermiso

MODULOS_SISTEMA = ['Clientes', 'Pagos', 'Usuarios', 'Inventario', 'Citas', 'Servicios', 'Consumo', 'Promos', 'Proveedores', 'Reportes', 'Bitacora']

@roles_bp.route('/listado')
@login_required
def listado_roles():
    if current_user.id_rol != 1:
        flash("Acceso denegado. Solo administradores pueden gestionar roles.", "danger")
        return redirect(url_for('acceso.dashboard'))
    
    search = request.args.get('search', '')
    estado_filter = request.args.get('estado', '')

    query = Rol.query

    if search:
        query = query.filter(Rol.nombre_rol.like(f'%{search}%'))
    
    if estado_filter:
        query = query.filter(Rol.estatus == estado_filter)

    roles = query.all()
    return render_template('roles/listadoroles.html', roles=roles, active_page='roles')

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def roles_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        tiene_permisos = False
        for mod in MODULOS_SISTEMA:
            if request.form.get(f'permiso_{mod}_1') or request.form.get(f'permiso_{mod}_2'):
                tiene_permisos = True
                break
        
        if not tiene_permisos:
            flash("Error: Debes seleccionar al menos un permiso para el rol.", "danger")
            return render_template('roles/formroles.html', editando=False)

        nuevo_rol = Rol(nombre_rol=nombre, descripcion=descripcion)
        
        try:
            db.session.add(nuevo_rol)
            db.session.flush()

            for mod in MODULOS_SISTEMA:
                if request.form.get(f'permiso_{mod}_1'):
                    p_leer = Permisos.query.filter_by(nombre_permisos=f"{mod}_1").first()
                    if p_leer: nuevo_rol.permisos.append(p_leer)
                if request.form.get(f'permiso_{mod}_2'):
                    p_esc = Permisos.query.filter_by(nombre_permisos=f"{mod}_2").first()
                    if p_esc: nuevo_rol.permisos.append(p_esc)

            db.session.commit()
            
            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="CREACION_ROL",
                modulo="Seguridad",
                detalle=f"Se creó el rol '{nombre}'."
            )
            
            flash("Rol creado exitosamente", "success")
            return redirect(url_for('roles.listado_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template('roles/formroles.html', editando=False)

@roles_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_rol(id):
    rol = Rol.query.get_or_404(id)

    # Función interna para checar si el rol ya tiene el permiso (para el HTML)
    def verificar_permiso(modulo_nombre, id_permiso):
        registro = RolPermiso.query.join(Modulo).filter(
            RolPermiso.id_rol == id,
            Modulo.nombre_modulo.ilike(f"%{modulo_nombre}%"),
            RolPermiso.id_permiso == id_permiso
        ).first()
        return registro is not None

    if request.method == 'POST':
        # 1. Validación: Al menos un permiso seleccionado
        tiene_permisos = False
        for mod in MODULOS_SISTEMA:
            if request.form.get(f'permiso_{mod}_1') or request.form.get(f'permiso_{mod}_2'):
                tiene_permisos = True
                break
        
        if not tiene_permisos:
            flash("Error: Debes seleccionar al menos un permiso.", "danger")
            return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso)

        try:
            rol.nombre_rol = request.form.get('nombre')
            rol.descripcion = request.form.get('descripcion')
            
            # Limpiar permisos actuales para reemplazarlos con los nuevos
            rol.permisos = [] 

            for mod in MODULOS_SISTEMA:
                if request.form.get(f'permiso_{mod}_1'):
                    p_leer = Permisos.query.filter_by(nombre_permisos=f"{mod}_1").first()
                    if p_leer: rol.permisos.append(p_leer)
                
                if request.form.get(f'permiso_{mod}_2'):
                    p_esc = Permisos.query.filter_by(nombre_permisos=f"{mod}_2").first()
                    if p_esc: rol.permisos.append(p_esc)

            db.session.commit()
            
            registrar_log(
                usuario_id=session.get('user_id'),
                accion="ACTUALIZACION_ROL",
                modulo="Seguridad",
                detalle=f"Se editó el rol: {rol.nombre_rol}"
            )
            flash("Rol actualizado correctamente", "success")
            return redirect(url_for('roles.listado_roles'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    
    return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso)

@roles_bp.route('/roles/desactivar/<int:id>')
@login_required
def confirmar_desactivar_rol(id):
    rol = Rol.query.get_or_404(id)
    return render_template('roles/eliminar_rol.html', rol=rol)

@roles_bp.route('/roles/eliminar_logico/<int:id>', methods=['POST'])
@login_required
def eliminar_rol_logico(id):
    if current_user.id_rol != 1:
        return redirect(url_for('acceso.dashboard'))
    
    rol = Rol.query.get_or_404(id)

    if rol.id_rol == 1:
        flash("No puedes desactivar el rol de Administrador principal.", "danger")
        return redirect(url_for('roles.listado_roles'))
    
    rol.estatus = 'INACTIVO'
    try:
        db.session.commit()
        registrar_log(usuario_id=session.get('user_id', 0), accion="BAJA_ROL", tabla="rol", registro_id=rol.id_rol, descripcion=f"Rol desactivado: {rol.nombre_rol}")
        flash('Rol desactivado correctamente', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('roles.listado_roles'))

@roles_bp.route('/ver/<int:id>')
@login_required
def ver_detalle_rol(id):
    rol = Rol.query.get_or_404(id)
    
    return render_template('roles/detalle_roles.html', rol=rol)