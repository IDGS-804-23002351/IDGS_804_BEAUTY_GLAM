from . import proveedor
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text
import re

# --- READ (LISTAR) ---
@proveedor.route("/proveedores", methods=['GET'])
def indexProveedores():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    id_tipo_proveedor = request.args.get('id_tipo_proveedor', None)
    
    try:
        query = text("CALL sp_listar_proveedores(:estatus, :id_tipo_proveedor, :buscar)")
        result = db.session.execute(query, {
            "estatus": estatus if estatus else None,
            "id_tipo_proveedor": int(id_tipo_proveedor) if id_tipo_proveedor and id_tipo_proveedor != '' else None,
            "buscar": buscar if buscar else None
        })
        lista_proveedores = result.fetchall()
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        create_form = forms.ProveedorForm()
        filtro_form = forms.FiltroProveedorForm()
        
        filtro_form.id_tipo_proveedor.choices = [('', 'Todos')] + [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        create_form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        return render_template("proveedores/listadoProveedores.html",
                             form=create_form,
                             filtro=filtro_form,
                             proveedores=lista_proveedores)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- FORMULARIO NUEVO PROVEEDOR ---
@proveedor.route("/proveedores/nuevo", methods=['GET'])
def nuevo_proveedor():
    form = forms.ProveedorForm()
    try:
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
    except Exception as e:
        print(f"Error cargando tipos: {e}")
        form.id_tipo_proveedor.choices = []
    return render_template("proveedores/formproveedores.html", form=form, accion='crear')

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
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", "danger")
        return render_template("proveedores/formproveedores.html", form=form, accion='crear')
    
    try:
        query = text("""
            CALL sp_crear_proveedor(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :rfc_empresa, :id_tipo_proveedor
            )
        """)
        
        result = db.session.execute(query, {
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
            "id_tipo_proveedor": form.id_tipo_proveedor.data
        })
        db.session.commit()
        
        # Obtener mensaje del SP
        try:
            mensaje = result.fetchone()
            if mensaje and mensaje[0]:
                flash(mensaje[0], "success")
            else:
                flash("Proveedor registrado exitosamente", "success")
        except:
            flash("Proveedor registrado exitosamente", "success")
        
        return redirect(url_for('proveedor.indexProveedores'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Extraer mensaje del SP
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            if "El correo ya esta registrado" in sp_message:
                flash("El correo electrónico ya está registrado en el sistema", "danger")
            elif "El telefono debe tener 10 digitos numericos" in sp_message:
                flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
            elif "El formato del correo no es valido" in sp_message:
                flash("El formato del correo electrónico no es válido", "danger")
            elif "El nombre es obligatorio" in sp_message:
                flash("El nombre es obligatorio", "danger")
            elif "Los apellidos son obligatorios" in sp_message:
                flash("Los apellidos son obligatorios", "danger")
            elif "Debe seleccionar un tipo de proveedor" in sp_message:
                flash("Debe seleccionar un tipo de proveedor", "danger")
            elif "El tipo de proveedor no existe" in sp_message:
                flash("El tipo de proveedor seleccionado no existe", "danger")
            else:
                flash(sp_message, "danger")
        else:
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("proveedores/formproveedores.html", form=form, accion='crear')

# --- VER PROVEEDOR ---
@proveedor.route("/proveedores/ver/<int:id>", methods=['GET'])
def ver_proveedor(id):
    try:
        query = text("CALL sp_obtener_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        proveedor_data = result.fetchone()
        
        if not proveedor_data:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('proveedor.indexProveedores'))
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        form = forms.ProveedorForm()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        form.estatus.data = proveedor_data.estatus_proveedor
        
        return render_template("proveedores/formproveedores.html", 
                             form=form, 
                             accion='ver',
                             proveedor=proveedor_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('proveedor.indexProveedores'))

# --- EDITAR PROVEEDOR ---
@proveedor.route("/proveedores/editar/<int:id>", methods=['GET'])
def editar_proveedor(id):
    try:
        query = text("CALL sp_obtener_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        proveedor_data = result.fetchone()
        
        if not proveedor_data:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('proveedor.indexProveedores'))
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        form = forms.ProveedorForm()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        form.estatus.data = proveedor_data.estatus_proveedor
        
        return render_template("proveedores/formproveedores.html", 
                             form=form, 
                             accion='editar',
                             proveedor=proveedor_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('proveedor.indexProveedores'))

# --- UPDATE (ACTUALIZAR) ---
@proveedor.route("/proveedores/actualizar/<int:id>", methods=['POST'])
def actualizar_proveedor(id):
    # Obtener datos directamente del formulario
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
    rfc_empresa = request.form.get('rfc_empresa', '')
    id_tipo_proveedor = request.form.get('id_tipo_proveedor')
    estatus = request.form.get('estatus', 'ACTIVO')
    
    # Validaciones manuales
    errores = []
    if not nombre:
        errores.append("El nombre es requerido")
    if not apellidos:
        errores.append("Los apellidos son requeridos")
    if not telefono:
        errores.append("El teléfono es requerido")
    if not correo:
        errores.append("El correo es requerido")
    if not id_tipo_proveedor or id_tipo_proveedor == '0':
        errores.append("Debe seleccionar un tipo de proveedor")
    
    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for('proveedor.editar_proveedor', id=id))
    
    try:
        query = text("""
            CALL sp_actualizar_proveedor(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :rfc_empresa, :id_tipo_proveedor, :estatus
            )
        """)
        
        result = db.session.execute(query, {
            "id": id,
            "nombre": nombre,
            "apellidos": apellidos,
            "telefono": telefono,
            "correo": correo,
            "direccion": direccion,
            "rfc_empresa": rfc_empresa if rfc_empresa else None,
            "id_tipo_proveedor": int(id_tipo_proveedor),
            "estatus": estatus
        })
        db.session.commit()
        
        # Intentar obtener mensaje del SP
        try:
            mensaje = result.fetchone()
            if mensaje and mensaje[0]:
                flash(mensaje[0], "success")
            else:
                flash("Proveedor actualizado exitosamente", "success")
        except:
            flash("Proveedor actualizado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Extraer mensaje del SP
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            if "El correo ya esta registrado por otro proveedor" in sp_message:
                flash("El correo electrónico ya está registrado por otro proveedor", "danger")
            elif "El telefono debe tener 10 digitos numericos" in sp_message:
                flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
            elif "El formato del correo no es valido" in sp_message:
                flash("El formato del correo electrónico no es válido", "danger")
            elif "Debe seleccionar un tipo de proveedor" in sp_message:
                flash("Debe seleccionar un tipo de proveedor", "danger")
            else:
                flash(sp_message, "danger")
        else:
            flash(f"Error al actualizar: {error_msg}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))

# --- DELETE (BORRADO LÓGICO) ---
@proveedor.route("/proveedores/eliminar/<int:id>", methods=['POST'])
def eliminar_proveedor(id):
    try:
        query = text("CALL sp_eliminar_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        db.session.commit()
        
        # Obtener mensaje del SP
        try:
            mensaje = result.fetchone()
            if mensaje and mensaje[0]:
                flash(mensaje[0], "success")
            else:
                flash("Proveedor desactivado correctamente", "success")
        except:
            flash("Proveedor desactivado correctamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Extraer mensaje del SP
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            if "tiene compras registradas" in sp_message:
                flash("No se puede desactivar el proveedor porque tiene compras registradas", "warning")
            elif "El proveedor no existe" in sp_message:
                flash("El proveedor no existe", "danger")
            else:
                flash(sp_message, "warning")
        else:
            flash(f"Error al desactivar: {error_msg}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))