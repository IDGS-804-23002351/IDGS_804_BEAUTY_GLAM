from . import proveedor
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text

# --- READ (LISTAR) ---
@proveedor.route("/proveedores", methods=['GET'])
def indexProveedores():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    id_tipo_proveedor = request.args.get('id_tipo_proveedor', None)
    
    try:
        # Llamar al procedimiento almacenado para listar proveedores
        query = text("CALL sp_listar_proveedores(:estatus, :id_tipo_proveedor, :buscar)")
        result = db.session.execute(query, {
            "estatus": estatus if estatus else None,
            "id_tipo_proveedor": int(id_tipo_proveedor) if id_tipo_proveedor and id_tipo_proveedor != '' else None,
            "buscar": buscar if buscar else None
        })
        lista_proveedores = result.fetchall()
        
        # Obtener tipos de proveedor para el filtro
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        create_form = forms.ProveedorForm()
        filtro_form = forms.FiltroProveedorForm()
        
        # Cargar opciones para el select de tipo proveedor
        filtro_form.id_tipo_proveedor.choices = [('', 'Todos')] + [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        create_form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        return render_template("proveedores/listadoProveedores.html",
                             form=create_form,
                             filtro=filtro_form,
                             proveedores=lista_proveedores)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- CREATE (CREAR) ---
@proveedor.route("/proveedores/crear", methods=['POST'])
def crear_proveedor():
    form = forms.ProveedorForm(request.form)
    
    # Cargar opciones para el select
    try:
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
    except:
        pass
    
    if form.validate_on_submit():
        try:
            query = text("""
                CALL sp_crear_proveedor(
                    :nombre, :apellidos, :telefono, :correo, 
                    :direccion, :rfc_empresa, :id_tipo_proveedor
                )
            """)
            
            db.session.execute(query, {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "telefono": form.telefono.data,
                "correo": form.correo.data,
                "direccion": form.direccion.data,
                "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
                "id_tipo_proveedor": form.id_tipo_proveedor.data
            })
            db.session.commit()
            flash("Proveedor registrado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
            
    return redirect(url_for('proveedor.indexProveedores'))

# --- UPDATE (ACTUALIZAR) ---
@proveedor.route("/proveedores/actualizar/<int:id>", methods=['POST'])
def actualizar_proveedor(id):
    form = forms.ProveedorForm(request.form)
    
    try:
        query = text("""
            CALL sp_actualizar_proveedor(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :rfc_empresa, :id_tipo_proveedor, :estatus
            )
        """)
        db.session.execute(query, {
            "id": id,
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
            "id_tipo_proveedor": form.id_tipo_proveedor.data,
            "estatus": request.form.get('estatus', 'ACTIVO')
        })
        db.session.commit()
        flash("Datos actualizados", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))

# --- DELETE (BORRADO LÓGICO) ---
@proveedor.route("/proveedores/eliminar/<int:id>", methods=['POST'])
def eliminar_proveedor(id):
    try:
        query = text("CALL sp_eliminar_proveedor(:id)")
        db.session.execute(query, {"id": id})
        db.session.commit()
        flash("Proveedor desactivado correctamente", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))

# --- OBTENER DATOS PARA EDITAR ---
@proveedor.route("/proveedores/editar/<int:id>", methods=['GET'])
def editar_proveedor(id):
    try:
        query = text("CALL sp_obtener_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        proveedor_data = result.fetchone()
        
        if not proveedor_data:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('proveedor.indexProveedores'))
        
        # Obtener tipos de proveedor
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        form = forms.ProveedorForm()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        # Llenar el formulario con los datos
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        
        # Filtro
        filtro_form = forms.FiltroProveedorForm()
        filtro_form.id_tipo_proveedor.choices = [('', 'Todos')] + [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        return render_template("proveedores/editarProveedor.html",
                             form=form,
                             filtro=filtro_form,
                             proveedor=proveedor_data,
                             id_proveedor=id)
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
        return redirect(url_for('proveedor.indexProveedores'))