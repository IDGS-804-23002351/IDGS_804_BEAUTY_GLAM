from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from . import roles_bp
from models import db, Rol, Permisos, registrar_log, Modulo, RolPermiso

MODULOS_SISTEMA = ['Clientes', 'Pagos', 'Usuarios', 'Inventario', 'Citas', 'Servicios', 'Consumo', 'Promos', 'Proveedores', 'Reportes', 'Bitacora']

@roles_bp.route('/listado')
@login_required
def listado_roles():
    roles = Rol.query.all()
    return render_template('roles/listadoroles.html', roles=roles, active_page='roles')

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def roles_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        # 1. Validación: Al menos un permiso seleccionado
        tiene_permisos = False
        for mod in MODULOS_SISTEMA:
            if request.form.get(f'permiso_{mod}_1') or request.form.get(f'permiso_{mod}_2'):
                tiene_permisos = True
                break
        
        if not tiene_permisos:
            flash("Error: Debes seleccionar al menos un permiso para el rol.", "danger")
            return render_template('roles/formroles.html', editando=False)

        # 2. Creación del Rol
        nuevo_rol = Rol(nombre_rol=nombre, descripcion=descripcion)
        
        try:
            db.session.add(nuevo_rol)
            db.session.flush() # Para obtener el ID antes del commit

            # 3. Asignación de permisos
            for mod in MODULOS_SISTEMA:
                # Lectura
                if request.form.get(f'permiso_{mod}_1'):
                    p_leer = Permisos.query.filter_by(nombre_permisos=f"{mod}_1").first()
                    if p_leer: nuevo_rol.permisos.append(p_leer)
                # Escritura
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