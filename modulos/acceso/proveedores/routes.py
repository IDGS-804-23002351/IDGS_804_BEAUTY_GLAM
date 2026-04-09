from . import proveedor
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re
from datetime import datetime

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
        form.genero.data = 'Sin especificar'
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
        contrasenia_hash = generate_password_hash(form.contrasenia.data)
        
        query = text("""
            CALL sp_crear_proveedor(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :rfc_empresa, :id_tipo_proveedor,
                :nombre_usuario, :contrasenia_hash,
                :fecha_nacimiento, :genero
            )
        """)
        
        result = db.session.execute(query, {
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
            "id_tipo_proveedor": form.id_tipo_proveedor.data,
            "nombre_usuario": form.nombre_usuario.data,
            "contrasenia_hash": contrasenia_hash,
            "fecha_nacimiento": form.fecha_nacimiento.data if form.fecha_nacimiento.data else None,
            "genero": form.genero.data if form.genero.data else 'Sin especificar'
        })
        db.session.commit()
        
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
        
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            flash(sp_message, "danger")
        else:
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("proveedores/formproveedores.html", form=form, accion='crear')

# --- VER PROVEEDOR ---
@proveedor.route("/proveedores/ver/<int:id>", methods=['GET'])
def ver_proveedor(id):
    modo = request.args.get('modo', 'ver')  # Por defecto 'ver'
    
    print(f"Modo recibido: {modo}")  # Para depurar en consola
    
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
        form.fecha_nacimiento.data = proveedor_data.fecha_nacimiento if hasattr(proveedor_data, 'fecha_nacimiento') else None
        form.genero.data = proveedor_data.genero if hasattr(proveedor_data, 'genero') else 'Sin especificar'
        form.nombre_usuario.data = proveedor_data.nombre_usuario if hasattr(proveedor_data, 'nombre_usuario') else ''
        
        return render_template("proveedores/formproveedores.html", 
                             form=form, 
                             accion='ver',
                             proveedor=proveedor_data,
                             modo=modo)  # Asegurar que se pasa el modo
        
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
        
        # Limpiar validadores de campos que no se usan en edición
        form.nombre_usuario.validators = []
        form.contrasenia.validators = []
        form.confirmar_contrasenia.validators = []
        
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        form.estatus.data = proveedor_data.estatus_proveedor
        form.fecha_nacimiento.data = proveedor_data.fecha_nacimiento if hasattr(proveedor_data, 'fecha_nacimiento') else None
        form.genero.data = proveedor_data.genero if hasattr(proveedor_data, 'genero') else 'Sin especificar'
        form.nombre_usuario.data = proveedor_data.nombre_usuario if hasattr(proveedor_data, 'nombre_usuario') else ''
        
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
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
    rfc_empresa = request.form.get('rfc_empresa', '')
    id_tipo_proveedor = request.form.get('id_tipo_proveedor')
    estatus = request.form.get('estatus', 'ACTIVO')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    genero = request.form.get('genero', 'Sin especificar')
    
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
                :correo, :direccion, :rfc_empresa, :id_tipo_proveedor, :estatus,
                :fecha_nacimiento, :genero
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
            "estatus": estatus,
            "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento else None,
            "genero": genero if genero else 'Sin especificar'
        })
        db.session.commit()
        
        flash("Proveedor actualizado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            flash(match.group(1), "danger")
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
        
        flash("Proveedor desactivado correctamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            if "tiene compras registradas" in sp_message:
                flash("No se puede desactivar el proveedor porque tiene compras registradas", "warning")
            else:
                flash(sp_message, "warning")
        else:
            flash(f"Error al desactivar: {error_msg}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))