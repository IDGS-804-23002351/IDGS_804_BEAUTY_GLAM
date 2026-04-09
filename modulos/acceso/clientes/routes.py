from . import clientes
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re
from models import registrar_historial_cliente, obtener_historial_cliente, registrar_log
# --- READ (LISTAR) ---
@clientes.route("/clientes", methods=['GET'])
def indexClientes():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    cliente_id = request.args.get('cliente_id', None, type=int)
    pagina_historial = request.args.get('pagina_historial', 1, type=int)
    
    try:
        # 1. Obtener listado de clientes
        query = text("CALL sp_listar_clientes(:estatus, :buscar)")
        result = db.session.execute(query, {"estatus": estatus, "buscar": buscar})
        resultados = result.fetchall()
        
        # Convertir los resultados a diccionarios
        lista_clientes = []
        for row in resultados:
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
        
        # 2. Obtener historial del cliente seleccionado
        historial_citas = []
        cliente_seleccionado = None
        total_historial = 0
        total_historial_paginas = 0
        por_pagina = 10
        
        if cliente_id:
            # Buscar el cliente seleccionado en la lista
            for cliente in lista_clientes:
                if cliente['id_cliente'] == cliente_id:
                    cliente_seleccionado = cliente
                    break
            
            if cliente_seleccionado:
                # Obtener historial de citas del cliente (como en la imagen)
                offset = (pagina_historial - 1) * por_pagina
                query_historial = text("""
                    SELECT 
                        DATE(c.fecha_hora) as fecha,
                        GROUP_CONCAT(DISTINCT s.nombre_servicio SEPARATOR ', ') as servicios,
                        SUM(dc.subtotal - IFNULL(dc.descuento, 0)) as total,
                        CONCAT(p.nombre_persona, ' ', p.apellidos) as empleado
                    FROM cita c
                    INNER JOIN detalle_cita dc ON c.id_cita = dc.id_cita
                    INNER JOIN servicio s ON dc.id_servicio = s.id_servicio
                    INNER JOIN empleado e ON c.id_empleado = e.id_empleado
                    INNER JOIN persona p ON e.id_persona = p.id_persona
                    WHERE c.id_cliente = :cliente_id 
                        AND c.estatus IN ('FINALIZADA', 'COMPLETADA')
                    GROUP BY c.id_cita, c.fecha_hora, p.nombre_persona, p.apellidos
                    ORDER BY c.fecha_hora DESC
                    LIMIT :limit OFFSET :offset
                """)
                
                result_historial = db.session.execute(query_historial, {
                    "cliente_id": cliente_id,
                    "limit": por_pagina,
                    "offset": offset
                })
                
                for row in result_historial:
                    historial_citas.append({
                        'fecha': row[0].strftime('%Y-%m-%d') if row[0] else 'N/A',
                        'servicio': row[1],
                        'total': f"{int(row[2]):,}" if row[2] else "0",
                        'empleado': row[3]
                    })
                
                # Contar total de citas del cliente
                query_count = text("""
                    SELECT COUNT(DISTINCT c.id_cita)
                    FROM cita c
                    WHERE c.id_cliente = :cliente_id 
                        AND c.estatus IN ('FINALIZADA', 'COMPLETADA')
                """)
                total_historial = db.session.execute(query_count, {"cliente_id": cliente_id}).scalar() or 0
                total_historial_paginas = (total_historial + por_pagina - 1) // por_pagina
        
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
                             estatus_actual=estatus,
                             cliente_seleccionado=cliente_seleccionado,
                             historial_citas=historial_citas,
                             historial_pagina=pagina_historial,
                             total_historial=total_historial,
                             total_historial_paginas=total_historial_paginas)
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
        
        # Obtener el ID del cliente recién creado
        cliente_id = None
        try:
            query_id = text("SELECT LAST_INSERT_ID()")
            result_id = db.session.execute(query_id)
            cliente_id = result_id.fetchone()[0]
        except:
            pass
        
        # Registrar en historial de cliente (MongoDB)
        if cliente_id:
            from flask_login import current_user
            datos_nuevos = {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "telefono": form.telefono.data,
                "correo": form.correo.data,
                "nombre_usuario": form.nombre_usuario.data
            }
            registrar_historial_cliente(
                usuario_id=current_user.id_usuario,
                cliente_id=cliente_id,
                accion="CREAR",
                detalle=f"Cliente {form.nombre.data} {form.apellidos.data} registrado",
                datos_nuevos=datos_nuevos
            )
        
        # Registrar en bitácora general
        registrar_log(
            usuario_id=current_user.id_usuario,
            accion="CREAR_CLIENTE",
            modulo="Clientes",
            detalle=f"Cliente {form.nombre.data} {form.apellidos.data} creado",
            tabla="cliente",
            registro_id=cliente_id
        )
        
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
    # Obtener datos actuales del cliente (para comparar después)
    try:
        query_actual = text("CALL sp_obtener_cliente(:id)")
        result_actual = db.session.execute(query_actual, {"id": id})
        cliente_actual = result_actual.fetchone()
    except:
        cliente_actual = None
    
    # Obtener datos del formulario
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion', '')
    estatus = request.form.get('estatus', 'ACTIVO')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    genero = request.form.get('genero', 'Sin especificar')
    
    # Crear formulario para mostrar errores
    form = forms.ClienteForm()
    
    # Limpiar validadores de campos que no se usan en edición
    form.nombre_usuario.validators = []
    form.contrasenia.validators = []
    form.confirmar_contrasenia.validators = []
    
    # Llenar el formulario con los datos enviados
    form.nombre.data = nombre
    form.apellidos.data = apellidos
    form.telefono.data = telefono
    form.correo.data = correo
    form.direccion.data = direccion
    form.estatus.data = estatus
    form.fecha_nacimiento.data = fecha_nacimiento if fecha_nacimiento else None
    form.genero.data = genero
    
    # Validaciones manuales
    errores = []
    if not nombre:
        errores.append("El nombre es requerido")
        form.nombre.errors.append("El nombre es requerido")
    if not apellidos:
        errores.append("Los apellidos son requeridos")
        form.apellidos.errors.append("Los apellidos son requeridos")
    if not telefono:
        errores.append("El teléfono es requerido")
        form.telefono.errors.append("El teléfono es requerido")
    if not correo:
        errores.append("El correo es requerido")
        form.correo.errors.append("El correo es requerido")
    
    # Validar teléfono (10 dígitos)
    if telefono and not re.match(r'^[0-9]{10}$', telefono):
        errores.append("El teléfono debe tener exactamente 10 dígitos numéricos")
        form.telefono.errors.append("El teléfono debe tener exactamente 10 dígitos numéricos")
    
    # Validar correo electrónico
    if correo and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
        errores.append("El formato del correo electrónico no es válido")
        form.correo.errors.append("El formato del correo electrónico no es válido")
    
    # Validar fecha de nacimiento
    if fecha_nacimiento:
        from datetime import datetime
        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            from datetime import date
            if fecha_nac > date.today():
                errores.append("La fecha de nacimiento no puede ser futura")
                form.fecha_nacimiento.errors.append("La fecha de nacimiento no puede ser futura")
            elif (date.today().year - fecha_nac.year) < 12:
                errores.append("El cliente debe ser mayor de 12 años")
                form.fecha_nacimiento.errors.append("El cliente debe ser mayor de 12 años")
        except:
            pass
    
    # Si hay errores, mostrar el formulario con los errores
    if errores:
        for error in errores:
            flash(error, "danger")
        try:
            query = text("CALL sp_obtener_cliente(:id)")
            result = db.session.execute(query, {"id": id})
            cliente_data = result.fetchone()
        except:
            cliente_data = None
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='editar',
                             cliente=cliente_data)
    
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
        
        # Registrar en historial de cliente (MongoDB)
        from flask_login import current_user
        datos_anteriores = {
            "nombre": cliente_actual.nombre_persona if cliente_actual else None,
            "apellidos": cliente_actual.apellidos if cliente_actual else None,
            "telefono": cliente_actual.telefono if cliente_actual else None,
            "correo": cliente_actual.correo if cliente_actual else None,
            "estatus": cliente_actual.estatus_cliente if cliente_actual else None
        }
        datos_nuevos = {
            "nombre": nombre,
            "apellidos": apellidos,
            "telefono": telefono,
            "correo": correo,
            "estatus": estatus
        }
        
        registrar_historial_cliente(
            usuario_id=current_user.id_usuario,
            cliente_id=id,
            accion="ACTUALIZAR",
            detalle=f"Cliente {nombre} {apellidos} actualizado",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
        
        # Registrar en bitácora general
        registrar_log(
            usuario_id=current_user.id_usuario,
            accion="ACTUALIZAR_CLIENTE",
            modulo="Clientes",
            detalle=f"Cliente {nombre} {apellidos} actualizado",
            tabla="cliente",
            registro_id=id
        )
        
        flash("Cliente actualizado exitosamente", "success")
        return redirect(url_for('clientes.indexClientes'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        match = re.search(r"\(1644,\s+'([^']+)'\)", error_msg)
        if match:
            sp_message = match.group(1)
            form.correo.errors.append(sp_message) if "correo" in sp_message.lower() else flash(sp_message, "danger")
        else:
            flash(f"Error al actualizar: {error_msg}", "danger")
        
        try:
            query = text("CALL sp_obtener_cliente(:id)")
            result = db.session.execute(query, {"id": id})
            cliente_data = result.fetchone()
        except:
            cliente_data = None
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='editar',
                             cliente=cliente_data)
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
        # Obtener datos del cliente
        query = text("CALL sp_obtener_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        cliente_data = result.fetchone()
        
        if not cliente_data:
            flash("Cliente no encontrado", "danger")
            return redirect(url_for('clientes.indexClientes'))
        
        # Obtener historial del cliente desde MongoDB
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 10
        offset = (pagina - 1) * por_pagina
        
        historial, total_historial = obtener_historial_cliente(id, limite=por_pagina, offset=offset)
        
        # Calcular total de páginas
        total_paginas = (total_historial + por_pagina - 1) // por_pagina
        
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
        
        # Registrar que se vio el cliente
        from flask_login import current_user
        registrar_historial_cliente(
            usuario_id=current_user.id_usuario,
            cliente_id=id,
            accion="VER",
            detalle=f"Consulta de información del cliente {cliente_data.nombre_persona} {cliente_data.apellidos}"
        )
        
        return render_template("clientes/vercliente.html", 
                             form=form, 
                             accion='ver',
                             cliente=cliente_data,
                             historial=historial,
                             pagina_actual=pagina,
                             total_paginas=total_paginas,
                             total_historial=total_historial)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))