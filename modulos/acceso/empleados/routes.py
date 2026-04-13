from . import empleado
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re
from flask_login import login_required, current_user 
from datetime import datetime
# Agrega esta importación al inicio del archivo
from forms import RestablecerContraseniaEmpleadoForm

def validar_fortaleza_contrasenia(contrasenia):
    """
    Valida que la contraseña cumpla con requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    errores = []
    
    if len(contrasenia) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres")
    
    if not re.search(r'[A-Z]', contrasenia):
        errores.append("La contraseña debe contener al menos una letra mayúscula")
    
    if not re.search(r'[a-z]', contrasenia):
        errores.append("La contraseña debe contener al menos una letra minúscula")
    
    if not re.search(r'\d', contrasenia):
        errores.append("La contraseña debe contener al menos un número")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasenia):
        errores.append("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\"':{}|<>)")
    
    return errores

@empleado.route("/empleados/restablecer-contrasenia/<int:id>", methods=['GET', 'POST'])
@login_required
def restablecer_contrasenia(id):
    """Permite restablecer la contraseña de un empleado"""
    form = RestablecerContraseniaEmpleadoForm()
    
    if form.validate_on_submit():
        try:
            contrasenia_hash = generate_password_hash(form.nueva_contrasenia.data, method='pbkdf2:sha256', salt_length=16)
            
            query = text("""
                UPDATE usuario u
                INNER JOIN empleado e ON u.id_usuario = e.id_usuario
                SET u.contrasenia = :contrasenia
                WHERE e.id_empleado = :empleado_id
            """)
            
            db.session.execute(query, {
                "contrasenia": contrasenia_hash,
                "empleado_id": id
            })
            db.session.commit()
            
            flash("Contraseña restablecida exitosamente", "success")
            # CAMBIADO: Redirige al listado de empleados
            return redirect(url_for('empleado.indexEmpleados'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al restablecer contraseña: {str(e)}", "danger")
    
    return render_template("empleados/restablecer_contrasenia.html", 
                         form=form,
                         empleado_id=id, 
                         active_page='empleados')

# --- READ (LISTAR) ---
@empleado.route("/empleados", methods=['GET'])
@login_required
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
                             empleados=lista_empleados,active_page='empleados')
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- FORMULARIO NUEVO EMPLEADO ---
@empleado.route("/empleados/nuevo", methods=['GET'])
@login_required
def nuevo_empleado():
    form = forms.EmpleadoForm()
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
        # Establecer fecha actual por defecto
        form.fecha_contratacion.data = datetime.now().date()
        
    except:
        pass
    return render_template("empleados/formempleados.html", form=form, accion='crear', datetime=datetime, active_page='empleados')
# --- CREATE (CREAR) ---
@empleado.route("/empleados/crear", methods=['POST'])
@login_required
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
    
    # IMPORTANTE: Si la fecha no viene en el POST, asignar la fecha actual
    if not form.fecha_contratacion.data:
        form.fecha_contratacion.data = datetime.now().date()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", "danger")
        return render_template("empleados/formempleados.html", form=form, accion='crear', datetime=datetime)
    
    # Validar fortaleza de la contraseña
    errores_contrasenia = validar_fortaleza_contrasenia(form.contrasenia.data)
    if errores_contrasenia:
        for error in errores_contrasenia:
            flash(f"Error en contraseña: {error}", "danger")
        return render_template("empleados/formempleados.html", form=form, accion='crear', datetime=datetime)
    
    # Validar que las contraseñas coincidan
    if form.contrasenia.data != form.confirmar_contrasenia.data:
        flash("Las contraseñas no coinciden", "danger")
        return render_template("empleados/formempleados.html", form=form, accion='crear', datetime=datetime)
    
    try:
        # Usar hash más seguro
        contrasenia_hash = generate_password_hash(form.contrasenia.data, method='pbkdf2:sha256', salt_length=16)
        
        query = text("""
            CALL sp_crear_empleado(
                :nombre, :apellidos, :telefono, :correo, 
                :direccion, :id_puesto, :fecha_contratacion, 
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
            "id_puesto": form.id_puesto.data,
            "fecha_contratacion": form.fecha_contratacion.data,
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
            flash("Empleado registrado exitosamente", "success")
        
        return redirect(url_for('empleado.indexEmpleados'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Buscar el mensaje personalizado del SP
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            flash(sp_message, "danger")
        else:
            flash(f"Error al registrar: {error_msg}", "danger")
        
        return render_template("empleados/formempleados.html", form=form, accion='crear', datetime=datetime, active_page='empleados')
# --- OBTENER DATOS PARA EDITAR ---
@empleado.route("/empleados/editar/<int:id>", methods=['GET'])
@login_required
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
        form.fecha_nacimiento.data = empleado_data.fecha_nacimiento
        form.genero.data = empleado_data.genero if hasattr(empleado_data, 'genero') else 'Sin especificar'
        
        return render_template("empleados/formempleados.html", form=form, accion='editar',empleado=empleado_data,active_page='empleados')
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
        return redirect(url_for('empleado.indexEmpleados'))
# --- UPDATE (ACTUALIZAR) ---
@empleado.route("/empleados/actualizar/<int:id>", methods=['POST'])
@login_required
def actualizar_empleado(id):
    # Obtener datos del formulario
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
    id_puesto = request.form.get('id_puesto')
    estatus = request.form.get('estatus', 'ACTIVO')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    genero = request.form.get('genero', 'Sin especificar')
    
    # Validaciones manuales
    errores = []
    
    # Validar nombre
    if not nombre:
        errores.append("El nombre es requerido")
    
    # Validar apellidos
    if not apellidos:
        errores.append("Los apellidos son requeridos")
    
    # Validar teléfono
    if not telefono:
        errores.append("El teléfono es requerido")
    elif not re.match(r'^[0-9]{10}$', telefono):
        errores.append("El teléfono debe tener exactamente 10 dígitos numéricos")
    
    # Validar correo
    if not correo:
        errores.append("El correo es requerido")
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
        errores.append("El formato del correo electrónico no es válido")
    
    # Validar puesto
    if not id_puesto or id_puesto == '0':
        errores.append("Debe seleccionar un puesto")
    
    # Validar fecha de nacimiento
    if fecha_nacimiento:
        from datetime import datetime
        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            from datetime import date
            if fecha_nac > date.today():
                errores.append("La fecha de nacimiento no puede ser futura")
            elif (date.today().year - fecha_nac.year) < 18:
                errores.append("El empleado debe ser mayor de 18 años")
        except:
            pass
    
    # VALIDAR GÉNERO
    generos_validos = ['Femenino', 'Masculino', 'Otro', 'Sin especificar']
    if not genero or genero == '':
        errores.append("Debe seleccionar un género")
    elif genero not in generos_validos:
        errores.append("El género no es válido. Seleccione: Femenino, Masculino, Otro o Sin especificar")
    
    # Si hay errores, mostrar mensajes y redirigir al formulario de edición
    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for('empleado.editar_empleado', id=id))
    
    try:
        # Asegurar que género tenga un valor válido
        if not genero or genero == '':
            genero = 'Sin especificar'
        
        query = text("""
            CALL sp_actualizar_empleado(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :id_puesto, :estatus,
                :fecha_nacimiento, :genero
            )
        """)
        
        result = db.session.execute(query, {
            "id": id,
            "nombre": nombre,
            "apellidos": apellidos,
            "telefono": telefono,
            "correo": correo,
            "direccion": direccion or '',
            "id_puesto": id_puesto,
            "estatus": estatus,
            "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento else None,
            "genero": genero
        })
        db.session.commit()
        
        flash("Empleado actualizado exitosamente", "success")
        return redirect(url_for('empleado.indexEmpleados'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Buscar mensaje del SP
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            flash(sp_message, "danger")
        elif "Data truncated for column 'genero'" in error_msg:
            flash("El género no es válido. Debe seleccionar: Femenino, Masculino, Otro o Sin especificar", "danger")
        else:
            flash(f"Error al actualizar: {error_msg}", "danger")
        
        return redirect(url_for('empleado.editar_empleado', id=id),active_page='empleados')
# --- DELETE (BORRADO LÓGICO) ---
@empleado.route("/empleados/eliminar/<int:id>", methods=['POST'])
@login_required
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
        
    return redirect(url_for('empleado.indexEmpleados'),active_page='empleados')

# --- VER EMPLEADO ---
@empleado.route("/empleados/ver/<int:id>", methods=['GET'])
@login_required
def ver_empleado(id):
    modo = request.args.get('modo', 'ver')  # 'ver' o 'desactivar'
    
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
        form.fecha_nacimiento.data = empleado_data.fecha_nacimiento
        form.genero.data = empleado_data.genero if hasattr(empleado_data, 'genero') else 'Sin especificar'

        return render_template("empleados/formempleados.html", 
                             form=form, 
                             accion='ver',
                             empleado=empleado_data,
                             modo=modo,active_page='empleados')  
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('empleado.indexEmpleados'))