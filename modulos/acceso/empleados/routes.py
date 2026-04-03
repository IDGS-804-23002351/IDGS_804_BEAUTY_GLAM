from . import empleado
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text

# --- READ (LISTAR) ---
@empleado.route("/empleados", methods=['GET'])
def indexEmpleados():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    id_puesto = request.args.get('id_puesto', None)
    
    try:
        query = text("CALL sp_listar_empleados(:estatus, :id_puesto, :buscar)")
        result = db.session.execute(query, {
            "estatus": estatus if estatus else None,
            "id_puesto": int(id_puesto) if id_puesto and id_puesto != '' else None,
            "buscar": buscar if buscar else None
        })
        lista_empleados = result.fetchall()
        
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        create_form = forms.EmpleadoForm()
        filtro_form = forms.FiltroEmpleadoForm()
        
        filtro_form.id_puesto.choices = [('', 'Todos')] + [(p.id_puesto, p.nombre_puesto) for p in puestos]
        create_form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
        return render_template("empleados/listadoEmpleados.html",
                             form=create_form,
                             filtro=filtro_form,
                             empleados=lista_empleados)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- FORMULARIO NUEVO EMPLEADO ---
@empleado.route("/empleados/nuevo", methods=['GET'])
def nuevo_empleado():
    form = forms.EmpleadoForm()
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
    except:
        pass
    return render_template("empleados/formempleados.html", form=form, accion='crear')

# --- CREATE (CREAR) ---
@empleado.route("/empleados/crear", methods=['POST'])
def crear_empleado():
    form = forms.EmpleadoForm(request.form)
    
    # Cargar opciones para el select
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
    except Exception as e:
        print(f"Error cargando puestos: {e}")
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", "danger")
        return render_template("empleados/formempleados.html", form=form, accion='crear')
    
    try:
        query = text("""
            CALL sp_crear_empleado(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :id_puesto, :fecha_contratacion, 
                :nombre_usuario, :contrasenia
            )
        """)
        
        result = db.session.execute(query, {
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "id_puesto": form.id_puesto.data,
            "fecha_contratacion": form.fecha_contratacion.data,
            "nombre_usuario": form.nombre_usuario.data,
            "contrasenia": form.contrasenia.data
        })
        db.session.commit()
        
        mensaje = result.fetchone()
        if mensaje:
            flash(mensaje[0], "success")
        else:
            flash("Empleado registrado exitosamente", "success")
        
        return redirect(url_for('empleado.indexEmpleados'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Extraer mensajes del SP
        if "El correo ya esta registrado" in error_msg:
            flash("El correo electrónico ya está registrado en el sistema", "danger")
        elif "El nombre de usuario ya esta en uso" in error_msg:
            flash("El nombre de usuario ya está en uso. Por favor elige otro", "danger")
        elif "La contrasenia debe tener al menos 6 caracteres" in error_msg:
            flash("La contraseña debe tener al menos 6 caracteres", "danger")
        elif "El telefono debe tener 10 digitos numericos" in error_msg:
            flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
        elif "El formato del correo no es valido" in error_msg:
            flash("El formato del correo electrónico no es válido", "danger")
        elif "El nombre es obligatorio" in error_msg:
            flash("El nombre es obligatorio", "danger")
        elif "Los apellidos son obligatorios" in error_msg:
            flash("Los apellidos son obligatorios", "danger")
        elif "La fecha de contratacion es obligatoria" in error_msg:
            flash("La fecha de contratación es obligatoria", "danger")
        elif "La fecha de contratacion no puede ser futura" in error_msg:
            flash("La fecha de contratación no puede ser futura", "danger")
        elif "Debe seleccionar un puesto valido" in error_msg:
            flash("Debe seleccionar un puesto válido", "danger")
        elif "El puesto seleccionado no existe" in error_msg:
            flash("El puesto seleccionado no existe", "danger")
        else:
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("empleados/formempleados.html", form=form, accion='crear')

# --- OBTENER DATOS PARA EDITAR ---
@empleado.route("/empleados/editar/<int:id>", methods=['GET'])
def editar_empleado(id):
    try:
        query = text("CALL sp_obtener_empleado(:id)")
        result = db.session.execute(query, {"id": id})
        empleado_data = result.fetchone()
        
        if not empleado_data:
            flash("Empleado no encontrado", "danger")
            return redirect(url_for('empleado.indexEmpleados'))
        
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        form = forms.EmpleadoForm()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
        # Limpiar validadores de campos que no se usan en edición
        form.nombre_usuario.validators = []
        form.contrasenia.validators = []
        form.confirmar_contrasenia.validators = []
        
        # Llenar el formulario con los datos
        form.nombre.data = empleado_data.nombre_persona
        form.apellidos.data = empleado_data.apellidos
        form.telefono.data = empleado_data.telefono
        form.correo.data = empleado_data.correo
        form.direccion.data = empleado_data.direccion
        form.id_puesto.data = empleado_data.id_puesto
        form.fecha_contratacion.data = empleado_data.fecha_contratacion
        form.nombre_usuario.data = empleado_data.nombre_usuario
        form.estatus.data = empleado_data.estatus_empleado
        
        return render_template("empleados/formempleados.html",
                             form=form,
                             accion='editar',
                             empleado=empleado_data)
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
        return redirect(url_for('empleado.indexEmpleados'))
# --- UPDATE (ACTUALIZAR) ---
@empleado.route("/empleados/actualizar/<int:id>", methods=['POST'])
def actualizar_empleado(id):
    form = forms.EmpleadoForm(request.form)
    
    # Cargar opciones para el select
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
    except:
        pass
    
    # Para edición, no validamos los campos que no están en el formulario
    # Validamos manualmente solo los campos requeridos en edición
    errores = []
    
    if not form.nombre.data:
        errores.append("El nombre es requerido")
    if not form.apellidos.data:
        errores.append("Los apellidos son requeridos")
    if not form.telefono.data:
        errores.append("El teléfono es requerido")
    if not form.correo.data:
        errores.append("El correo es requerido")
    if not form.id_puesto.data or form.id_puesto.data == 0:
        errores.append("Debe seleccionar un puesto")
    
    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for('empleado.editar_empleado', id=id))
    
    try:
        query = text("""
            CALL sp_actualizar_empleado(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :id_puesto, :estatus
            )
        """)
        
        # Obtener el estatus del formulario o usar ACTIVO por defecto
        estatus = request.form.get('estatus', 'ACTIVO')
        
        result = db.session.execute(query, {
            "id": id,
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data or '',
            "id_puesto": form.id_puesto.data,
            "estatus": estatus
        })
        db.session.commit()
        
        # Intentar obtener mensaje del SP
        try:
            mensaje = result.fetchone()
            if mensaje and mensaje[0]:
                flash(mensaje[0], "success")
            else:
                flash("Empleado actualizado exitosamente", "success")
        except:
            flash("Empleado actualizado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        if "El correo ya esta registrado por otro empleado" in error_msg:
            flash("El correo electrónico ya está registrado por otro empleado", "danger")
        elif "El telefono debe tener 10 digitos numericos" in error_msg:
            flash("El teléfono debe tener exactamente 10 dígitos numéricos", "danger")
        elif "El formato del correo no es valido" in error_msg:
            flash("El formato del correo electrónico no es válido", "danger")
        elif "Debe seleccionar un puesto valido" in error_msg:
            flash("Debe seleccionar un puesto válido", "danger")
        else:
            flash(f"Error al actualizar: {error_msg}", "danger")
        
    return redirect(url_for('empleado.indexEmpleados'))
# --- DELETE (BORRADO LÓGICO) ---
@empleado.route("/empleados/eliminar/<int:id>", methods=['POST'])
def eliminar_empleado(id):
    try:
        query = text("CALL sp_eliminar_empleado(:id)")
        result = db.session.execute(query, {"id": id})
        db.session.commit()
        
        mensaje = result.fetchone()
        if mensaje:
            flash(mensaje[0], "success")
        else:
            flash("Empleado desactivado correctamente", "success")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        if "tiene citas pendientes o confirmadas" in error_msg:
            flash("No se puede desactivar el empleado porque tiene citas pendientes o confirmadas", "warning")
        elif "El empleado no existe" in error_msg:
            flash("El empleado no existe", "danger")
        else:
            flash(f"Error al desactivar: {error_msg}", "danger")
        
    return redirect(url_for('empleado.indexEmpleados'))

# --- VER EMPLEADO ---
@empleado.route("/empleados/ver/<int:id>", methods=['GET'])
def ver_empleado(id):
    try:
        query = text("CALL sp_obtener_empleado(:id)")
        result = db.session.execute(query, {"id": id})
        empleado_data = result.fetchone()
        
        if not empleado_data:
            flash("Empleado no encontrado", "danger")
            return redirect(url_for('empleado.indexEmpleados'))
        
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        form = forms.EmpleadoForm()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
        form.nombre.data = empleado_data.nombre_persona
        form.apellidos.data = empleado_data.apellidos
        form.telefono.data = empleado_data.telefono
        form.correo.data = empleado_data.correo
        form.direccion.data = empleado_data.direccion
        form.id_puesto.data = empleado_data.id_puesto
        form.fecha_contratacion.data = empleado_data.fecha_contratacion
        form.nombre_usuario.data = empleado_data.nombre_usuario
        form.estatus.data = empleado_data.estatus_empleado
        
        return render_template("empleados/formempleados.html", 
                             form=form, 
                             accion='ver',
                             empleado=empleado_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('empleado.indexEmpleados'))