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
        # Llamar al procedimiento almacenado para listar empleados
        query = text("CALL sp_listar_empleados(:estatus, :id_puesto, :buscar)")
        result = db.session.execute(query, {
            "estatus": estatus if estatus else None,
            "id_puesto": int(id_puesto) if id_puesto and id_puesto != '' else None,
            "buscar": buscar if buscar else None
        })
        lista_empleados = result.fetchall()
        
        # Obtener puestos para el filtro
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        create_form = forms.EmpleadoForm()
        filtro_form = forms.FiltroEmpleadoForm()
        
        # Cargar opciones para los selects
        filtro_form.id_puesto.choices = [('', 'Todos')] + [(p.id_puesto, p.nombre_puesto) for p in puestos]
        create_form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
        return render_template("empleados/listadoEmpleados.html",
                             form=create_form,
                             filtro=filtro_form,
                             empleados=lista_empleados)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- CREATE (CREAR) ---
@empleado.route("/empleados/crear", methods=['POST'])
def crear_empleado():
    form = forms.EmpleadoForm(request.form)
    
    print("=== CREANDO EMPLEADO ===")
    print(f"Datos recibidos: {request.form}")
    
    # Cargar opciones para el select
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
    except Exception as e:
        print(f"Error cargando puestos: {e}")
    
    if form.validate_on_submit():
        print("Formulario validado correctamente")
        print(f"Nombre: {form.nombre.data}")
        print(f"Apellidos: {form.apellidos.data}")
        print(f"Teléfono: {form.telefono.data}")
        print(f"Correo: {form.correo.data}")
        print(f"Dirección: {form.direccion.data}")
        print(f"ID Puesto: {form.id_puesto.data}")
        print(f"Fecha Contratación: {form.fecha_contratacion.data}")
        print(f"Usuario: {form.nombre_usuario.data}")
        print(f"Contraseña: {form.contrasenia.data}")
        
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
            print("SP ejecutado correctamente")
            flash("Empleado registrado exitosamente", "success")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR DETALLADO: {str(e)}")
            flash(f"Error: {str(e)}", "danger")
    else:
        print("Formulario NO válido")
        print(f"Errores: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
            
    return redirect(url_for('empleado.indexEmpleados'))
# --- FORMULARIO NUEVO EMPLEADO ---
@empleado.route("/empleados/nuevo", methods=['GET'])
def nuevo_empleado():
    form = forms.EmpleadoForm()
    # Cargar opciones para el select
    try:
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
    except:
        pass
    return render_template("empleados/formempleados.html", form=form, accion='crear')
# --- UPDATE (ACTUALIZAR) ---
@empleado.route("/empleados/actualizar/<int:id>", methods=['POST'])
def actualizar_empleado(id):
    form = forms.EmpleadoForm(request.form)
    
    try:
        query = text("""
            CALL sp_actualizar_empleado(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :id_puesto, :estatus
            )
        """)
        db.session.execute(query, {
            "id": id,
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "id_puesto": form.id_puesto.data,
            "estatus": request.form.get('estatus', 'ACTIVO')
        })
        db.session.commit()
        flash("Datos actualizados", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        
    return redirect(url_for('empleado.indexEmpleados'))

# --- DELETE (BORRADO LÓGICO) ---
@empleado.route("/empleados/eliminar/<int:id>", methods=['POST'])
def eliminar_empleado(id):
    try:
        query = text("CALL sp_eliminar_empleado(:id)")
        db.session.execute(query, {"id": id})
        db.session.commit()
        flash("Empleado desactivado correctamente", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        
    return redirect(url_for('empleado.indexEmpleados'))

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
        
        # Obtener puestos
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        form = forms.EmpleadoForm()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
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
        
        # Usar el mismo template formempleados.html con accion='editar'
        return render_template("empleados/formempleados.html",
                             form=form,
                             accion='editar',
                             empleado=empleado_data)
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
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
        
        # Obtener puestos para el select
        puestos_query = text("CALL sp_listar_puestos()")
        puestos_result = db.session.execute(puestos_query)
        puestos = puestos_result.fetchall()
        
        form = forms.EmpleadoForm()
        form.id_puesto.choices = [(p.id_puesto, p.nombre_puesto) for p in puestos]
        
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
                             accion='ver',
                             empleado=empleado_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('empleado.indexEmpleados'))