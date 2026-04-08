from . import clientes
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re

# --- READ (LISTAR) ---
@clientes.route("/clientes", methods=['GET'])
def indexClientes():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    
    try:
        query = text("CALL sp_listar_clientes(:estatus, :buscar)")
        result = db.session.execute(query, {"estatus": estatus, "buscar": buscar})
        resultados = result.fetchall()
        
        # Convertir los resultados a diccionarios para acceso por nombre
        lista_clientes = []
        for row in resultados:
            # Convertir Row a diccionario
            cliente_dict = {
                'id_cliente': row[0],
                'nombre_completo': row[1],
                'telefono': row[2],
                'correo': row[3],
                'estatus_cliente': row[4],
                'nombre_usuario': row[5],
                'total_citas': row[6]
            }
            lista_clientes.append(cliente_dict)
        
        # Mostrar mensaje si no hay clientes
        if not lista_clientes:
            if buscar:
                flash(f"No se encontraron clientes que coincidan con '{buscar}'", "info")
            elif estatus:
                flash(f"No hay clientes con estatus '{estatus}'", "info")
            else:
                flash("No hay clientes registrados en el sistema", "info")
        
        create_form = forms.ClienteForm() 
        return render_template("clientes/listadoclientes.html",
                             form=create_form, 
                             clientes=lista_clientes,
                             buscar_actual=buscar,
                             estatus_actual=estatus)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('acceso.login'))

# --- FORMULARIO NUEVO CLIENTE ---
@clientes.route("/clientes/nuevo", methods=['GET'])
def nuevo_cliente():
    form = forms.ClienteForm()
    form.genero.data = 'Sin especificar'
    return render_template("clientes/formclientes.html", form=form, accion='crear')

# --- FORMULARIO EDITAR CLIENTE ---
@clientes.route("/clientes/editar/<int:id>", methods=['GET'])
def editar_cliente(id):
    try:
        query = text("CALL sp_obtener_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        cliente_data = result.fetchone()
        
        if not cliente_data:
            flash("Cliente no encontrado", "danger")
            return redirect(url_for('clientes.indexClientes'))
        
        form = forms.ClienteForm()
        
        # Limpiar validadores de campos que no se usan en edición
        form.nombre_usuario.validators = []
        form.contrasenia.validators = []
        form.confirmar_contrasenia.validators = []
        
        form.id.data = cliente_data.id_cliente
        form.nombre.data = cliente_data.nombre_persona
        form.apellidos.data = cliente_data.apellidos
        form.telefono.data = cliente_data.telefono
        form.correo.data = cliente_data.correo
        form.direccion.data = cliente_data.direccion
        form.nombre_usuario.data = cliente_data.nombre_usuario
        form.estatus.data = cliente_data.estatus_cliente
        form.fecha_nacimiento.data = cliente_data.fecha_nacimiento
        form.genero.data = cliente_data.genero if hasattr(cliente_data, 'genero') else 'Sin especificar'
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='editar',
                             cliente=cliente_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))
# --- CREATE (CREAR) ---
@clientes.route("/clientes/crear", methods=['POST'])
def crear_cliente():
    form = forms.ClienteForm(request.form)
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", "danger")
        return render_template("clientes/formclientes.html", form=form, accion='crear')
    
    try:
        contrasenia_hash = generate_password_hash(form.contrasenia.data)
        
        query = text("""
            CALL sp_crear_cliente(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :nombre_usuario, :contrasenia_hash,
                :fecha_nacimiento, :genero
            )
        """)
        
        result = db.session.execute(query, {
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "nombre_usuario": form.nombre_usuario.data,  
            "contrasenia_hash": contrasenia_hash,
            "fecha_nacimiento": form.fecha_nacimiento.data if form.fecha_nacimiento.data else None,
            "genero": form.genero.data if form.genero.data else 'Sin especificar'
        })
        db.session.commit()
        
        mensaje = result.fetchone()
        if mensaje:
            flash(mensaje[0], "success")
        else:
            flash("Cliente registrado exitosamente", "success")
        
        return redirect(url_for('clientes.indexClientes'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            flash(sp_message, "danger")
        else:
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("clientes/formclientes.html", form=form, accion='crear')
# --- UPDATE (ACTUALIZAR) ---
@clientes.route("/clientes/actualizar/<int:id>", methods=['POST'])
def actualizar_cliente(id):
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
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
    
    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for('clientes.editar_cliente', id=id))
    
    try:
        query = text("""
            CALL sp_actualizar_cliente(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :estatus,
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
            "estatus": estatus,
            "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento else None,
            "genero": genero
        })
        db.session.commit()
        
        flash("Cliente actualizado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        flash(f"Error al actualizar: {error_msg}", "danger")
        
    return redirect(url_for('clientes.indexClientes'))
# --- DELETE (BORRADO LÓGICO) ---
@clientes.route("/clientes/eliminar/<int:id>", methods=['POST'])
def eliminar_cliente(id):
    try:
        query = text("CALL sp_eliminar_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        db.session.commit()
        
        mensaje = result.fetchone()
        if mensaje:
            flash(mensaje[0], "success")
        else:
            flash("Cliente desactivado correctamente", "success")
        
        # Agregar mensaje de confirmación adicional
        flash("La operación se completó exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Extraer el mensaje original del SP
        import re
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            if "tiene citas pendientes o confirmadas" in sp_message:
                flash("No se puede desactivar el cliente porque tiene citas pendientes o confirmadas", "warning")
            elif "El cliente no existe" in sp_message:
                flash("El cliente no existe en el sistema", "danger")
            else:
                flash(f"{sp_message}", "warning")
        else:
            flash(f"Error al desactivar: {error_msg}", "danger")
        
    return redirect(url_for('clientes.indexClientes'))
# --- VER CLIENTE ---
@clientes.route("/clientes/ver/<int:id>", methods=['GET'])
def ver_cliente(id):
    try:
        query = text("CALL sp_obtener_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        cliente_data = result.fetchone()
        
        if not cliente_data:
            flash("Cliente no encontrado", "danger")
            return redirect(url_for('clientes.indexClientes'))
        
        form = forms.ClienteForm()
        form.id.data = cliente_data.id_cliente
        form.nombre.data = cliente_data.nombre_persona
        form.apellidos.data = cliente_data.apellidos
        form.telefono.data = cliente_data.telefono
        form.correo.data = cliente_data.correo
        form.direccion.data = cliente_data.direccion
        form.nombre_usuario.data = cliente_data.nombre_usuario
        form.estatus.data = cliente_data.estatus_cliente
        form.fecha_nacimiento.data = cliente_data.fecha_nacimiento
        form.genero.data = cliente_data.genero if hasattr(cliente_data, 'genero') else 'Sin especificar'
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='ver',
                             cliente=cliente_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))