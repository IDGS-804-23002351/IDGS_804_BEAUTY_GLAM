from . import clientes
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text

# --- READ (LISTAR) ---
@clientes.route("/clientes", methods=['GET'])
def indexClientes():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    
    try:
        query = text("CALL sp_listar_clientes(:estatus, :buscar)")
        result = db.session.execute(query, {"estatus": estatus, "buscar": buscar})
        lista_clientes = result.fetchall()
        
        create_form = forms.ClienteForm() 
        return render_template("clientes/listadoclientes.html",
                             form=create_form, 
                             clientes=lista_clientes)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('acceso.login'))

# --- FORMULARIO NUEVO CLIENTE ---
@clientes.route("/clientes/nuevo", methods=['GET'])
def nuevo_cliente():
    form = forms.ClienteForm()
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
        query = text("""
            CALL sp_crear_cliente(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :nombre_usuario, :contrasenia
            )
        """)
        
        result = db.session.execute(query, {
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "nombre_usuario": form.nombre_usuario.data,  
            "contrasenia": form.contrasenia.data       
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
        
        # Extraer el mensaje original del SP (está dentro del error)
        # Buscar el mensaje entre comillas o después del código de error
        import re
        
        # Buscar el mensaje personalizado del SP (está después del número 1644)
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            
            # Mostrar mensajes amigables según el error del SP
            if "El correo ya esta registrado" in sp_message:
                flash("El correo electrónico ya está registrado en el sistema", "danger")
            elif "El nombre de usuario ya esta en uso" in sp_message:
                flash("El nombre de usuario ya está en uso. Por favor elige otro", "danger")
            elif "La contrasenia debe tener al menos 6 caracteres" in sp_message:
                flash("La contraseña debe tener al menos 6 caracteres", "danger")
            elif "El telefono debe tener 10 digitos numericos" in sp_message:
                flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
            elif "El formato del correo no es valido" in sp_message:
                flash("El formato del correo electrónico no es válido", "danger")
            elif "El nombre es obligatorio" in sp_message:
                flash("El nombre es obligatorio", "danger")
            elif "Los apellidos son obligatorios" in sp_message:
                flash("Los apellidos son obligatorios", "danger")
            else:
                flash(sp_message, "danger")
        else:
            # Si no se encuentra el mensaje del SP, mostrar el error genérico
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("clientes/formclientes.html", form=form, accion='crear')

# --- UPDATE (ACTUALIZAR) ---
@clientes.route("/clientes/actualizar/<int:id>", methods=['POST'])
def actualizar_cliente(id):
    # Obtener datos directamente del formulario
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
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
    
    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for('clientes.editar_cliente', id=id))
    
    try:
        query = text("""
            CALL sp_actualizar_cliente(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :estatus
            )
        """)
        
        result = db.session.execute(query, {
            "id": id,
            "nombre": nombre,
            "apellidos": apellidos,
            "telefono": telefono,
            "correo": correo,
            "direccion": direccion,
            "estatus": estatus
        })
        db.session.commit()
        
        # Intentar obtener mensaje del SP
        try:
            mensaje = result.fetchone()
            if mensaje and mensaje[0]:
                flash(mensaje[0], "success")
            else:
                flash("Cliente actualizado exitosamente", "success")
        except:
            flash("Cliente actualizado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        if "El correo ya esta registrado por otro cliente" in error_msg:
            flash("El correo electrónico ya está registrado por otro cliente", "danger")
        elif "El telefono debe tener 10 digitos numericos" in error_msg:
            flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
        elif "El formato del correo no es valido" in error_msg:
            flash("El formato del correo electrónico no es válido", "danger")
        else:
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
                flash("El cliente no existe", "danger")
            else:
                flash(sp_message, "warning")
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
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='ver',
                             cliente=cliente_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))