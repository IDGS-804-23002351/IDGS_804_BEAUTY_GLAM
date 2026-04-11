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
    
    search = request.args.get('search', '').strip()
    estado_filter = request.args.get('estado', '')

    query = Rol.query

    if search:
        query = query.filter(Rol.nombre_rol.ilike(f'%{search}%'))
    
    if estado_filter:
        query = query.filter(Rol.estatus == estado_filter)

    roles = query.all()
    
    return render_template('roles/listadoroles.html', roles=roles, active_page='roles',search_valor=search, estado_valor=estado_filter)

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def roles_form():
    if current_user.id_rol != 1:
        flash("Acceso denegado.", "danger")
        return redirect(url_for('acceso.dashboard'))

    def verificar_en_post(modulo_nombre, id_permiso):
        return request.form.get(f'permiso_{modulo_nombre}_{id_permiso}') is not None

    rol_data = None 

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        rol_data = Rol(nombre_rol=nombre, descripcion=descripcion)

        if not nombre:
            flash("El nombre del rol es obligatorio.", "danger")
            return render_template('roles/formroles.html', rol=rol_data, editando=False, check=verificar_en_post)
        
        if not descripcion:
            flash("La descripción es obligatoria.", "danger")
            return render_template('roles/formroles.html', rol=rol_data, editando=False, check=verificar_en_post)

        permisos_seleccionados = []
        for mod in MODULOS_SISTEMA:
            if request.form.get(f'permiso_{mod}_1'): permisos_seleccionados.append(f"{mod}_1")
            if request.form.get(f'permiso_{mod}_2'): permisos_seleccionados.append(f"{mod}_2")
        
        if not permisos_seleccionados:
            flash("Error: Debes seleccionar al menos un permiso.", "danger")
            return render_template('roles/formroles.html', rol=rol_data, editando=False, check=verificar_en_post)

        try:
            nuevo_rol = Rol(nombre_rol=nombre, descripcion=descripcion)
            db.session.add(nuevo_rol)
            db.session.flush()

            for nombre_p in permisos_seleccionados:
                p_db = Permisos.query.filter_by(nombre_permisos=nombre_p).first()
                if p_db: nuevo_rol.permisos.append(p_db)

            db.session.commit()
            flash("Rol creado exitosamente", "success")
            return redirect(url_for('roles.listado_roles'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template('roles/formroles.html', rol=rol_data, editando=False, check=verificar_en_post)

@roles_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_rol(id):
    rol = Rol.query.get_or_404(id)

    # Helper para mantener los checkboxes marcados si la validación falla
    def verificar_permiso_hibrido(modulo_nombre, id_permiso):
        if request.method == 'POST':
            return request.form.get(f'permiso_{modulo_nombre}_{id_permiso}') is not None
        nombre_buscado = f"{modulo_nombre}_{id_permiso}"
        return any(p.nombre_permisos == nombre_buscado for p in rol.permisos)

    if request.method == 'POST':
        # 1. Obtener y limpiar datos
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        # 2. Validaciones de texto (Retorno temprano si fallan)
        if not nombre:
            flash("El nombre del rol es obligatorio.", "danger")
            rol.descripcion = descripcion # Mantener lo que escribió en descripción
            return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso_hibrido)

        if not descripcion:
            flash("La descripción es obligatoria.", "danger")
            rol.nombre_rol = nombre # Mantener lo que escribió en nombre
            return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso_hibrido)

        # 3. Validación de Permisos
        permisos_seleccionados = []
        for mod in MODULOS_SISTEMA:
            if request.form.get(f'permiso_{mod}_1'): permisos_seleccionados.append(f"{mod}_1")
            if request.form.get(f'permiso_{mod}_2'): permisos_seleccionados.append(f"{mod}_2")
        
        if not permisos_seleccionados:
            flash("Error: Debes seleccionar al menos un permiso para el rol.", "danger")
            rol.nombre_rol = nombre
            rol.descripcion = descripcion
            return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso_hibrido)

        # 4. Intento de guardado en Base de Datos
        try:
            rol.nombre_rol = nombre
            rol.descripcion = descripcion
            
            # Limpiamos permisos actuales y asignamos los nuevos
            rol.permisos = [] 
            for nombre_p in permisos_seleccionados:
                p_db = Permisos.query.filter_by(nombre_permisos=nombre_p).first()
                if p_db: 
                    rol.permisos.append(p_db)

            db.session.commit()
            flash("Rol actualizado correctamente", "success")
            return redirect(url_for('roles.listado_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error de base de datos: {str(e)}", "danger")
    
    # Si es GET, simplemente mostramos el form con los datos de la DB
    return render_template('roles/formroles.html', rol=rol, editando=True, check=verificar_permiso_hibrido)

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