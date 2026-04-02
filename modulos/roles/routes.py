from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from . import roles_bp
from models import db, Rol, Permisos, registrar_log, Modulo, RolPermiso

@roles_bp.route('/listado')
def listado_roles():
    roles = Rol.query.all()
    return render_template('roles/listadoroles.html', roles=roles, active_page='roles')

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
def roles_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        nuevo_rol = Rol(nombre_rol=nombre, descripcion=descripcion)
        
        try:
            db.session.add(nuevo_rol)
            db.session.flush() 

            modulos_sistema = ['Clientes', 'Pagos', 'Usuarios', 'Inventario', 'Bitacora']
            
            for mod in modulos_sistema:
                nivel = request.form.get(f'permiso_{mod}')
                if nivel:
                    nuevo_permiso = Permisos(
                        nombre_permisos=f"{mod}_{nivel}", 
                    )
                    db.session.add(nuevo_permiso)
                    nuevo_rol.permisos.append(nuevo_permiso)

            db.session.commit()
            
            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="CREACION_ROL",
                tabla_final="Seguridad",
                desc_final=f"Se creó el rol '{nombre}' con sus privilegios."
            )
            
            flash("Rol y permisos creados exitosamente", "success")
            return redirect(url_for('roles.listado_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template('roles/formroles.html')

@roles_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_rol(id):
    rol = Rol.query.get_or_404(id)

    def verificar_permiso(modulo_nombre, permiso_buscado):
        registro = RolPermiso.query.join(Modulo).filter(
            RolPermiso.id_rol == id,
            Modulo.nombre == modulo_nombre,
            RolPermiso.id_permiso == permiso_buscado
        ).first()
        
        # Devolvemos True si encontramos el registro (tiene ese permiso)
        return registro is not None
    
    if request.method == 'POST':
        rol.nombre_rol = request.form.get('nombre')
        rol.descripcion = request.form.get('descripcion')
        
        try:
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