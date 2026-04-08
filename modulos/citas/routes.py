from flask import render_template, request, redirect, url_for, flash, session
from decimal import Decimal
from datetime import datetime
from flask_login import login_required, current_user
from . import citas_bp
import forms
from models import db
from sqlalchemy import or_, func 
from datetime import datetime, timedelta
from models import (
    Cita, Cliente, Empleado, Persona, Servicio, DetalleCita, Pago,
    MovimientoInventario, InsumoServicio, Producto, registrar_log
)


def ejecutar_consumo_automatico(id_cita):
    detalles = db.session.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()

    movimientos_generados = []

    for detalle in detalles:
        servicio = db.session.query(Servicio).filter(
            Servicio.id_servicio == detalle.id_servicio
        ).first()

        if not servicio:
            continue

        insumos = db.session.query(InsumoServicio).filter(
            InsumoServicio.id_servicio == servicio.id_servicio
        ).all()

        for insumo in insumos:
            producto = db.session.query(Producto).filter(
                Producto.codigo_producto == insumo.codigo_producto
            ).first()

            if not producto:
                continue

            motivo_movimiento = f"CONSUMO AUTO | CITA:{id_cita} | DETALLE:{detalle.id_detalle_cita} | SERVICIO:{servicio.nombre_servicio}"

            ya_existe = db.session.query(MovimientoInventario).filter(
                MovimientoInventario.codigo_producto == producto.codigo_producto,
                MovimientoInventario.tipo == 'SALIDA',
                MovimientoInventario.motivo == motivo_movimiento
            ).first()

            if ya_existe:
                continue

            cantidad_consumo = Decimal(str(
                insumo.cantidad_utilizada if insumo.cantidad_utilizada is not None else 0
            ))
            stock_actual = Decimal(str(
                producto.stock_actual if producto.stock_actual is not None else 0
            ))

            if stock_actual < cantidad_consumo:
                producto.stock_actual = Decimal('0.00')
            else:
                producto.stock_actual = stock_actual - cantidad_consumo

            movimiento = MovimientoInventario(
                codigo_producto=producto.codigo_producto,
                tipo='SALIDA',
                cantidad=cantidad_consumo,
                motivo=motivo_movimiento
            )
            db.session.add(movimiento)

            movimientos_generados.append({
                'codigo_producto': producto.codigo_producto,
                'cantidad': cantidad_consumo,
                'motivo': motivo_movimiento
            })

    return movimientos_generados


def obtener_total_cita(id_cita):
    detalles = db.session.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()

    total = Decimal('0.00')

    for detalle in detalles:
        if detalle.subtotal:
            total += Decimal(str(detalle.subtotal))

    return total


def obtener_total_pagado_cita(id_cita):
    pagos = db.session.query(Pago).filter(Pago.id_cita == id_cita).all()
    total_pagado = Decimal('0.00')

    for pago in pagos:
        if pago.total:
            total_pagado += Decimal(str(pago.total))

    return total_pagado


def obtener_estado_pago_cita(id_cita):
    total_cita = obtener_total_cita(id_cita)
    total_pagado = obtener_total_pagado_cita(id_cita)
    faltante = total_cita - total_pagado

    if faltante < 0:
        faltante = Decimal('0.00')

    if total_pagado == 0:
        estado_pago = 'SIN PAGO'
    elif total_pagado < total_cita:
        estado_pago = 'ANTICIPO'
    else:
        estado_pago = 'PAGADA'

    return {
        'total_cita': total_cita,
        'total_pagado': total_pagado,
        'faltante': faltante,
        'estado_pago': estado_pago
    }


@citas_bp.route('/citas', methods=['GET', 'POST'])
def listado_citas():
    filtro_form = forms.FiltroCitaForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()

    filtro_form.id_cliente.choices = [(0, 'Todos')] + [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if hasattr(c, 'persona') and c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    filtro_form.id_empleado.choices = [(0, 'Todos')] + [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if hasattr(e, 'persona') and e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    query = db.session.query(Cita)

    estatus = request.args.get('estatus', '')
    id_cliente = request.args.get('id_cliente', '0')
    id_empleado = request.args.get('id_empleado', '0')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')

    if estatus:
        query = query.filter(Cita.estatus == estatus)

    if id_cliente and id_cliente != '0':
        query = query.filter(Cita.id_cliente == int(id_cliente))

    if id_empleado and id_empleado != '0':
        query = query.filter(Cita.id_empleado == int(id_empleado))

    if fecha_inicio:
        query = query.filter(Cita.fecha_hora >= fecha_inicio + " 00:00:00")

    if fecha_fin:
        query = query.filter(Cita.fecha_hora <= fecha_fin + " 23:59:59")

    citas = query.order_by(Cita.fecha_hora.desc()).all()

    citas_data = []

    for c in citas:
        cliente = db.session.query(Cliente).filter(Cliente.id_cliente == c.id_cliente).first()
        empleado = db.session.query(Empleado).filter(Empleado.id_empleado == c.id_empleado).first()

        persona_cliente = db.session.query(Persona).filter(Persona.id_persona == cliente.id_persona).first() if cliente else None
        persona_empleado = db.session.query(Persona).filter(Persona.id_persona == empleado.id_persona).first() if empleado else None

        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_cita == c.id_cita).first()
        servicio = db.session.query(Servicio).filter(Servicio.id_servicio == detalle.id_servicio).first() if detalle else None

        info_pago = obtener_estado_pago_cita(c.id_cita)

        citas_data.append({
            'id_cita': c.id_cita,
            'cliente': f"{persona_cliente.nombre_persona} {persona_cliente.apellidos}" if persona_cliente else 'Sin cliente',
            'empleado': f"{persona_empleado.nombre_persona} {persona_empleado.apellidos}" if persona_empleado else 'Sin empleado',
            'servicio': servicio.nombre_servicio if servicio else 'Sin servicio',
            'fecha_hora': c.fecha_hora,
            'estatus': c.estatus,
            'estado_pago': info_pago['estado_pago'],
            'total_cita': info_pago['total_cita'],
            'total_pagado': info_pago['total_pagado'],
            'faltante': info_pago['faltante']
        })

    return render_template(
        'citas/listado_citas.html',
        form=filtro_form,
        citas=citas_data,
        active_page='citas'
    )


@citas_bp.route('/citas/nueva', methods=['GET', 'POST'])
def nueva_cita():
    cita_form = forms.CitaForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    cita_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if hasattr(c, 'persona') and c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    cita_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if hasattr(e, 'persona') and e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    cita_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    if cita_form.validate_on_submit():
        if cita_form.fecha_hora.data < datetime.now():
            flash('No se pueden agendar citas en fechas pasadas', 'danger')
            return render_template('citas/cita_form.html', form=cita_form, active_page='citas')

        hora = cita_form.fecha_hora.data.time()
        if hora.hour < 9 or hora.hour > 20:
            flash('La cita debe estar dentro del horario laboral (9:00 a 20:00)', 'danger')
            return render_template('citas/cita_form.html', form=cita_form, active_page='citas')

        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == cita_form.id_empleado.data,
            Cita.fecha_hora == cita_form.fecha_hora.data,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ese horario ya está ocupado para el empleado seleccionado', 'danger')
            return render_template('citas/cita_form.html', form=cita_form, active_page='citas')

        nueva_cita = Cita(
            fecha_hora=cita_form.fecha_hora.data,
            estatus=cita_form.estatus.data,
            id_cliente=cita_form.id_cliente.data,
            id_empleado=cita_form.id_empleado.data
        )

        try:
            db.session.add(nueva_cita)
            db.session.flush()

            servicio = db.session.query(Servicio).filter(
                Servicio.id_servicio == cita_form.id_servicio.data
            ).first()

            if servicio:
                detalle = DetalleCita(
                    id_cita=nueva_cita.id_cita,
                    id_servicio=servicio.id_servicio,
                    subtotal=servicio.precio,
                    descuento=0
                )
                db.session.add(detalle)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_CITA",
                tabla="cita",
                registro_id=nueva_cita.id_cita,
                descripcion=f"Se registró la cita ID {nueva_cita.id_cita} para cliente {nueva_cita.id_cliente} con empleado {nueva_cita.id_empleado}"
            )

            flash('Cita registrada correctamente', 'success')
            return redirect(url_for('citas_bp.listado_citas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar cita: {str(e)}', 'danger')

    return render_template('citas/cita_form.html', form=cita_form, active_page='citas')


@citas_bp.route('/citas/detalle', methods=['GET'])
def detalle_cita():
    id = request.args.get('id')
    cita = db.session.query(Cita).filter(Cita.id_cita == id).first()

    if not cita:
        flash('Cita no encontrada', 'danger')
        return redirect(url_for('citas_bp.listado_citas'))

    cliente = db.session.query(Cliente).filter(Cliente.id_cliente == cita.id_cliente).first()
    empleado = db.session.query(Empleado).filter(Empleado.id_empleado == cita.id_empleado).first()

    persona_cliente = db.session.query(Persona).filter(Persona.id_persona == cliente.id_persona).first() if cliente else None
    persona_empleado = db.session.query(Persona).filter(Persona.id_persona == empleado.id_persona).first() if empleado else None

    detalles = db.session.query(DetalleCita).filter(DetalleCita.id_cita == cita.id_cita).all()

    servicios_data = []
    for d in detalles:
        servicio = db.session.query(Servicio).filter(Servicio.id_servicio == d.id_servicio).first()
        servicios_data.append({
            'nombre_servicio': servicio.nombre_servicio if servicio else 'Servicio',
            'subtotal': d.subtotal,
            'descuento': d.descuento
        })

    info_pago = obtener_estado_pago_cita(cita.id_cita)

    return render_template(
        'citas/detalle_citas.html',
        cita=cita,
        cliente=f"{persona_cliente.nombre_persona} {persona_cliente.apellidos}" if persona_cliente else 'Sin cliente',
        empleado=f"{persona_empleado.nombre_persona} {persona_empleado.apellidos}" if persona_empleado else 'Sin empleado',
        servicios=servicios_data,
        info_pago=info_pago,
        active_page='citas'
    )


@citas_bp.route('/citas/editar', methods=['GET', 'POST'])
def editar_cita():
    cita_form = forms.CitaForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    cita_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if hasattr(c, 'persona') and c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    cita_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if hasattr(e, 'persona') and e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    cita_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    if request.method == 'GET':
        id = request.args.get('id')
        cita = db.session.query(Cita).filter(Cita.id_cita == id).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_cita == cita.id_cita).first()

        cita_form.id.data = cita.id_cita
        cita_form.id_cliente.data = cita.id_cliente
        cita_form.id_empleado.data = cita.id_empleado
        cita_form.fecha_hora.data = cita.fecha_hora
        cita_form.estatus.data = cita.estatus
        cita_form.id_servicio.data = detalle.id_servicio if detalle else None

    if cita_form.validate_on_submit():
        cita = db.session.query(Cita).filter(Cita.id_cita == cita_form.id.data).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == cita_form.id_empleado.data,
            Cita.fecha_hora == cita_form.fecha_hora.data,
            Cita.id_cita != cita.id_cita,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ese horario ya está ocupado para el empleado seleccionado', 'danger')
            return render_template('citas/cita_form.html', form=cita_form, active_page='citas')

        estatus_anterior = cita.estatus

        try:
            cita.id_cliente = cita_form.id_cliente.data
            cita.id_empleado = cita_form.id_empleado.data
            cita.fecha_hora = cita_form.fecha_hora.data
            cita.estatus = cita_form.estatus.data

            db.session.query(DetalleCita).filter(
                DetalleCita.id_cita == cita.id_cita
            ).delete()

            servicio = db.session.query(Servicio).filter(
                Servicio.id_servicio == cita_form.id_servicio.data
            ).first()

            if servicio:
                detalle = DetalleCita(
                    id_cita=cita.id_cita,
                    id_servicio=servicio.id_servicio,
                    subtotal=servicio.precio,
                    descuento=0
                )
                db.session.add(detalle)
                db.session.flush()

            movimientos_generados = []
            if estatus_anterior != 'FINALIZADA' and cita.estatus == 'FINALIZADA':
                movimientos_generados = ejecutar_consumo_automatico(cita.id_cita)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_CITA",
                tabla="cita",
                registro_id=cita.id_cita,
                descripcion=f"Se modificó la cita ID {cita.id_cita}. Nuevo estatus: {cita.estatus}"
            )

            if estatus_anterior != 'FINALIZADA' and cita.estatus == 'FINALIZADA':
                registrar_log(
                    session.get('user_id', 0),
                    "FINALIZACION_CITA",
                    tabla="cita",
                    registro_id=cita.id_cita,
                    descripcion=f"Se finalizó la cita ID {cita.id_cita}"
                )

                for mov in movimientos_generados:
                    registrar_log(
                        session.get('user_id', 0),
                        "CONSUMO_AUTOMATICO",
                        tabla="movimiento_inventario",
                        registro_id=0,
                        descripcion=f"Consumo automático del producto {mov['codigo_producto']} por cantidad {mov['cantidad']} en cita {cita.id_cita}"
                    )

            flash('Cita modificada correctamente', 'success')
            return redirect(url_for('citas_bp.listado_citas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar cita: {str(e)}', 'danger')

    return render_template('citas/cita_form.html', form=cita_form, active_page='citas')


@citas_bp.route('/citas/eliminar', methods=['GET', 'POST'])
def eliminar_cita():
    cita_form = forms.CitaForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    cita_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if hasattr(c, 'persona') and c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    cita_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if hasattr(e, 'persona') and e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    cita_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    cita = None

    if request.method == 'GET':
        id = request.args.get('id')
        cita = db.session.query(Cita).filter(Cita.id_cita == id).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_cita == cita.id_cita).first()

        cita_form.id.data = cita.id_cita
        cita_form.id_cliente.data = cita.id_cliente
        cita_form.id_empleado.data = cita.id_empleado
        cita_form.fecha_hora.data = cita.fecha_hora
        cita_form.estatus.data = cita.estatus
        cita_form.id_servicio.data = detalle.id_servicio if detalle else None

        return render_template(
            'citas/eliminar_cita.html',
            form=cita_form,
            cita=cita,
            active_page='citas'
        )

    id_cita = request.form.get('id')
    cita = db.session.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita:
        flash('Cita no encontrada', 'danger')
        return redirect(url_for('citas_bp.listado_citas'))

    try:
        cita.estatus = 'CANCELADA'
        db.session.commit()

        registrar_log(
            session.get('user_id', 0),
            "CANCELACION_CITA",
            tabla="cita",
            registro_id=cita.id_cita,
            descripcion=f"Se canceló la cita ID {cita.id_cita}"
        )

        flash('Cita cancelada correctamente', 'warning')
        return redirect(url_for('citas_bp.listado_citas'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar: {str(e)}', 'danger')
        return redirect(url_for('citas_bp.listado_citas'))

@citas_bp.route('/citas/agendar', methods=['GET', 'POST'])
@login_required
def agendar_cita():
    """Vista para que los clientes agenden citas"""
    
    # Obtener el cliente actual
    cliente_actual = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if not cliente_actual:
        flash('Debes completar tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))
    
    # Obtener servicios activos
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()
    
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        id_servicio = request.form.get('id_servicio')
        notas = request.form.get('notas', '')  # notas no se usa en el modelo, pero puedes guardarlo después
        
        # Validaciones
        if not fecha or not hora or not id_servicio:
            flash('Todos los campos son requeridos', 'danger')
            return redirect(url_for('citas_bp.agendar_cita'))
        
        try:
            # Combinar fecha y hora
            fecha_hora_cita = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
            
            # Validar que no sea fecha pasada
            if fecha_hora_cita < datetime.now():
                flash('No se pueden agendar citas en fechas u horarios pasados', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))
            
            # Validar horario laboral
            hora_cita = fecha_hora_cita.time()
            if hora_cita.hour < 9 or hora_cita.hour > 20:
                flash('La cita debe estar dentro del horario laboral (9:00 a 20:00 hrs)', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))
            
            # Crear la cita
            nueva_cita = Cita(
                fecha_hora=fecha_hora_cita,
                estatus='PENDIENTE',
                id_cliente=cliente_actual.id_cliente,
                id_empleado=None
            )
            
            db.session.add(nueva_cita)
            db.session.flush()  # Para obtener el ID de la cita
            
            # Agregar el servicio seleccionado
            servicio = Servicio.query.get(int(id_servicio))
            if servicio:
                detalle = DetalleCita(
                    id_cita=nueva_cita.id_cita,
                    id_servicio=servicio.id_servicio,
                    subtotal=servicio.precio,  # ← Usamos subtotal, no cantidad/precio_unitario
                    descuento=0
                )
                db.session.add(detalle)
            else:
                flash('El servicio seleccionado no existe', 'danger')
                db.session.rollback()
                return redirect(url_for('citas_bp.agendar_cita'))
            
            db.session.commit()
            
            registrar_log(
                current_user.id_usuario,
                "AGENDAR_CITA",
                "citas",
                f"Cita #{nueva_cita.id_cita} agendada para {fecha_hora_cita}"
            )
            
            flash(f'Cita agendada exitosamente para {fecha_hora_cita.strftime("%d/%m/%Y %H:%M")}', 'success')
            return redirect(url_for('citas_bp.mis_citas_cliente'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {str(e)}")  # Para depuración
            flash(f'Error al agendar la cita: {str(e)}', 'danger')
    
    return render_template('vistaClientes/citas/agendar_cita.html', 
                         cliente_actual=cliente_actual,
                         servicios=servicios,
                         datetime=datetime)
@citas_bp.route('/citas/mis-citas')
@login_required
def mis_citas_cliente():
    """Vista de citas para clientes"""
    cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if not cliente:
        flash('No se encontró tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))
    
    citas = Cita.query.filter_by(id_cliente=cliente.id_cliente).order_by(Cita.fecha_hora.desc()).all()
    
    citas_data = []
    for cita in citas:
        # Obtener servicios
        detalles = DetalleCita.query.filter_by(id_cita=cita.id_cita).all()
        servicio_nombre = "Múltiples"
        if len(detalles) == 1:
            servicio = Servicio.query.get(detalles[0].id_servicio)
            servicio_nombre = servicio.nombre_servicio if servicio else "Servicio"
        
        total = db.session.query(func.sum(DetalleCita.subtotal)).filter_by(id_cita=cita.id_cita).scalar() or 0
        
        # Verificar si hay pago
        pago = Pago.query.filter_by(id_cita=cita.id_cita).first()
        estado_pago = 'PAGADO' if pago else 'PENDIENTE'
        
        citas_data.append({
            'id_cita': cita.id_cita,
            'fecha_hora': cita.fecha_hora,
            'estatus': cita.estatus,
            'servicio_nombre': servicio_nombre,
            'total': float(total),
            'estado_pago': estado_pago
        })
    
    return render_template('vistaClientes/citas/mis_citas_cliente.html', citas=citas_data)


@citas_bp.route('/citas/detalle-cliente')
@login_required
def detalle_cita_cliente():
    """Detalle de cita para cliente"""
    id = request.args.get('id')
    cita = Cita.query.get_or_404(id)
    
    cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if cita.id_cliente != cliente.id_cliente:
        flash('No tienes permiso para ver esta cita', 'danger')
        return redirect(url_for('citas_bp.mis_citas_cliente'))
    
    detalles = db.session.query(
        DetalleCita, Servicio.nombre_servicio, Servicio.precio
    ).join(Servicio, DetalleCita.id_servicio == Servicio.id_servicio)\
     .filter(DetalleCita.id_cita == id).all()
    
    pago = Pago.query.filter_by(id_cita=id).first()
    
    total = sum(d.subtotal for d, _, _ in detalles)
    
    return render_template('vistaClientes/citas/detalle_cita_cliente.html',
                         cita=cita, detalles=detalles, pago=pago, total=total)


@citas_bp.route('/citas/cancelar-cliente/<int:id>')
@login_required
def cancelar_cita_cliente(id):
    """Cancelar cita para cliente"""
    cita = Cita.query.get_or_404(id)
    cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if cita.id_cliente != cliente.id_cliente:
        flash('No tienes permiso para cancelar esta cita', 'danger')
        return redirect(url_for('citas_bp.mis_citas_cliente'))
    
    if cita.estatus in ['PENDIENTE', 'CONFIRMADA']:
        # Cambiar el estado a CANCELADA
        cita.estatus = 'CANCELADA'
        db.session.commit()
        
        registrar_log(
            current_user.id_usuario, 
            'CANCELAR_CITA', 
            'citas', 
            f'Cita #{id} cancelada por el cliente'
        )
        
        flash('Cita cancelada exitosamente', 'success')
    else:
        flash('No se puede cancelar esta cita porque ya está ' + cita.estatus.lower(), 'warning')
    
    # Redirigir a Mis Citas
    return redirect(url_for('citas_bp.mis_citas_cliente'))