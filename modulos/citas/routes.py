from flask import render_template, request, redirect, url_for, flash, session
from decimal import Decimal
from datetime import datetime, timedelta, time
from flask_login import login_required, current_user
from sqlalchemy import func

from . import citas_bp
import forms
from models import db
from models import (
    Cita, Cliente, Empleado, Persona, Servicio, Promocion, DetalleCita, Pago,
    MovimientoInventario, InsumoServicio, Producto, Usuario, registrar_log,Puesto
)


def usuario_es_admin():
    return str(session.get('user_rol', '')).strip().upper() == 'ADMINISTRADOR'


def obtener_empleado_logueado():
    user_id = session.get('user_id', 0)

    usuario = db.session.query(Usuario).filter(
        Usuario.id_usuario == user_id
    ).first()

    if not usuario:
        return None

    if not hasattr(usuario, 'id_persona') or not usuario.id_persona:
        return None

    empleado = db.session.query(Empleado).filter(
        Empleado.id_persona == usuario.id_persona
    ).first()

    return empleado


def obtener_cliente_logueado():
    cliente = None

    if hasattr(Cliente, 'id_usuario') and hasattr(current_user, 'id_usuario'):
        cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()

    if not cliente and hasattr(current_user, 'id_persona') and hasattr(Cliente, 'id_persona'):
        cliente = Cliente.query.filter_by(id_persona=current_user.id_persona).first()

    return cliente


def obtener_nombre_persona_por_empleado(empleado):
    if not empleado:
        return 'Sin empleado'

    if hasattr(empleado, 'persona') and empleado.persona:
        return f"{empleado.persona.nombre_persona} {empleado.persona.apellidos}"

    persona = db.session.query(Persona).filter(
        Persona.id_persona == empleado.id_persona
    ).first()

    if persona:
        return f"{persona.nombre_persona} {persona.apellidos}"

    return f"Empleado {empleado.id_empleado}"


def obtener_nombre_persona_por_cliente(cliente):
    if not cliente:
        return 'Sin cliente'

    if hasattr(cliente, 'persona') and cliente.persona:
        return f"{cliente.persona.nombre_persona} {cliente.persona.apellidos}"

    persona = db.session.query(Persona).filter(
        Persona.id_persona == cliente.id_persona
    ).first()

    if persona:
        return f"{persona.nombre_persona} {persona.apellidos}"

    return f"Cliente {cliente.id_cliente}"


def descomponer_seleccion_item(valor):
    if not valor or '-' not in valor:
        return None, None

    partes = valor.split('-', 1)

    if len(partes) != 2:
        return None, None

    tipo = partes[0].strip().upper()

    try:
        identificador = int(partes[1])
    except ValueError:
        return None, None

    return tipo, identificador


def ejecutar_consumo_automatico(id_cita):
    detalles = db.session.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()

    movimientos_generados = []

    for detalle in detalles:
        if not detalle.id_servicio:
            continue

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

            motivo_movimiento = (
                f"CONSUMO AUTO | CITA:{id_cita} | "
                f"DETALLE:{detalle.id_detalle_cita} | "
                f"SERVICIO:{servicio.nombre_servicio}"
            )

            ya_existe = db.session.query(MovimientoInventario).filter(
                MovimientoInventario.codigo_producto == producto.codigo_producto,
                MovimientoInventario.tipo == 'SALIDA',
                MovimientoInventario.motivo == motivo_movimiento
            ).first()

            if ya_existe:
                continue

            cantidad_consumo = Decimal(str(
                insumo.cantidad_utilizada if insumo.cantidad_utilizada is not None else 0
            )).quantize(Decimal('0.01'))

            stock_actual = Decimal(str(
                producto.stock_actual if producto.stock_actual is not None else 0
            )).quantize(Decimal('0.01'))

            if stock_actual < cantidad_consumo:
                raise ValueError(
                    f"No hay stock suficiente para {producto.nombre}. "
                    f"Stock actual: {stock_actual}, requerido: {cantidad_consumo}"
                )

            producto.stock_actual = (stock_actual - cantidad_consumo).quantize(Decimal('0.01'))

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


def revertir_consumo_automatico(id_cita):
    movimientos = db.session.query(MovimientoInventario).filter(
        MovimientoInventario.tipo == 'SALIDA',
        MovimientoInventario.motivo.like(f"CONSUMO AUTO | CITA:{id_cita} |%")
    ).all()

    movimientos_revertidos = []

    for movimiento in movimientos:
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == movimiento.codigo_producto
        ).first()

        if producto:
            stock_actual = Decimal(str(
                producto.stock_actual if producto.stock_actual is not None else 0
            )).quantize(Decimal('0.01'))

            cantidad_mov = Decimal(str(
                movimiento.cantidad if movimiento.cantidad is not None else 0
            )).quantize(Decimal('0.01'))

            producto.stock_actual = (stock_actual + cantidad_mov).quantize(Decimal('0.01'))

            movimientos_revertidos.append({
                'codigo_producto': movimiento.codigo_producto,
                'cantidad': cantidad_mov,
                'motivo': movimiento.motivo
            })

        db.session.delete(movimiento)

    return movimientos_revertidos


def obtener_total_cita(id_cita):
    detalles = db.session.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()

    total = Decimal('0.00')

    for detalle in detalles:
        subtotal = Decimal(str(detalle.subtotal if detalle.subtotal is not None else 0))
        descuento = Decimal(str(detalle.descuento if detalle.descuento is not None else 0))
        total += (subtotal - descuento)

    if total < 0:
        total = Decimal('0.00')

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

    if total_pagado >= total_cita and total_cita > 0:
        return 'PAGADA'

    return 'SIN PAGO'


def obtener_nombre_servicio_o_promocion(detalle):
    if not detalle:
        return 'Sin servicio'

    if detalle.id_servicio:
        servicio = db.session.query(Servicio).filter(
            Servicio.id_servicio == detalle.id_servicio
        ).first()
        return servicio.nombre_servicio if servicio else 'Servicio'

    if detalle.id_promocion:
        promocion = db.session.query(Promocion).filter(
            Promocion.id_promocion == detalle.id_promocion
        ).first()
        return promocion.nombre if promocion else 'Promoción'

    return 'Sin servicio'


def obtener_item_servicio_o_promocion(tipo_seleccion, id_seleccion):
    if tipo_seleccion == 'SERVICIO':
        servicio = db.session.query(Servicio).filter(
            Servicio.id_servicio == id_seleccion,
            Servicio.estatus == 'ACTIVO'
        ).first()

        if servicio:
            return {
                'id_servicio': servicio.id_servicio,
                'id_promocion': None,
                'subtotal': Decimal(str(servicio.precio if servicio.precio is not None else 0)),
                'descuento': Decimal('0.00')
            }

    elif tipo_seleccion == 'PROMOCION':
        promocion = db.session.query(Promocion).filter(
            Promocion.id_promocion == id_seleccion,
            Promocion.estatus == 'ACTIVO'
        ).first()

        if promocion:
            return {
                'id_servicio': None,
                'id_promocion': promocion.id_promocion,
                'subtotal': Decimal(str(promocion.valor_descuento if promocion.valor_descuento is not None else 0)),
                'descuento': Decimal('0.00')
            }

    return None


def validar_stock_servicio(id_servicio):
    servicio = db.session.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        return False, 'El servicio seleccionado no existe.'

    insumos = db.session.query(InsumoServicio).filter(
        InsumoServicio.id_servicio == id_servicio
    ).all()

    if not insumos:
        return False, f'El servicio {servicio.nombre_servicio} no tiene insumos registrados.'

    faltantes = []

    for insumo in insumos:
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == insumo.codigo_producto
        ).first()

        if not producto:
            faltantes.append(
                f"No existe el producto con código {insumo.codigo_producto} configurado para el servicio {servicio.nombre_servicio}"
            )
            continue

        stock_actual = Decimal(str(producto.stock_actual if producto.stock_actual is not None else 0)).quantize(Decimal('0.01'))
        cantidad_requerida = Decimal(str(insumo.cantidad_utilizada if insumo.cantidad_utilizada is not None else 0)).quantize(Decimal('0.01'))

        if stock_actual < cantidad_requerida:
            faltantes.append(
                f"No hay insumo suficiente para el servicio {servicio.nombre_servicio}: "
                f"{producto.nombre} (stock actual: {stock_actual}, requerido: {cantidad_requerida})"
            )

    if faltantes:
        return False, " | ".join(faltantes)

    return True, ''


def validar_stock_item(tipo_seleccion, id_seleccion):
    if tipo_seleccion == 'SERVICIO':
        return validar_stock_servicio(id_seleccion)

    if tipo_seleccion == 'PROMOCION':
        return True, ''

    return False, 'Debes seleccionar un servicio válido.'


def cargar_opciones_formulario_cita(cita_form):
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()
    promociones = Promocion.query.filter(Promocion.estatus == 'ACTIVO').all()

    cita_form.id_cliente.choices = [
        (c.id_cliente, obtener_nombre_persona_por_cliente(c))
        for c in clientes
    ]

    cita_form.id_empleado.choices = [
        (e.id_empleado, obtener_nombre_persona_por_empleado(e))
        for e in empleados
    ]

    cita_form.id_servicio.choices = []

    for s in servicios:
        cita_form.id_servicio.choices.append(
            (f"SERVICIO-{s.id_servicio}", f"{s.nombre_servicio}")
        )

    for p in promociones:
        cita_form.id_servicio.choices.append(
            (f"PROMOCION-{p.id_promocion}", f"Promoción | {p.nombre}")
        )


def ajustar_formulario_para_empleado_logueado(cita_form):
    if usuario_es_admin():
        return None

    empleado_logueado = obtener_empleado_logueado()

    if not empleado_logueado:
        return None

    cita_form.id_empleado.choices = [
        (empleado_logueado.id_empleado, obtener_nombre_persona_por_empleado(empleado_logueado))
    ]

    return empleado_logueado


@citas_bp.route('/citas', methods=['GET', 'POST'])
@login_required
def listado_citas():
    filtro_form = forms.FiltroCitaForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()

    filtro_form.id_cliente.choices = [(0, 'Todos')] + [
        (c.id_cliente, obtener_nombre_persona_por_cliente(c))
        for c in clientes
    ]

    filtro_form.id_empleado.choices = [(0, 'Todos')] + [
        (e.id_empleado, obtener_nombre_persona_por_empleado(e))
        for e in empleados
    ]

    query = db.session.query(Cita)

    estatus = request.args.get('estatus', '')
    id_cliente = request.args.get('id_cliente', '0')
    id_empleado = request.args.get('id_empleado', '0')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')

    if not usuario_es_admin():
        empleado_logueado = obtener_empleado_logueado()

        if empleado_logueado:
            query = query.filter(Cita.id_empleado == empleado_logueado.id_empleado)
            query = query.filter(Cita.estatus.in_(['PENDIENTE', 'CONFIRMADA']))
        else:
            query = query.filter(Cita.id_cita == -1)

    if estatus:
        query = query.filter(Cita.estatus == estatus)

    if id_cliente and id_cliente != '0':
        try:
            query = query.filter(Cita.id_cliente == int(id_cliente))
        except ValueError:
            pass

    if usuario_es_admin() and id_empleado and id_empleado != '0':
        try:
            query = query.filter(Cita.id_empleado == int(id_empleado))
        except ValueError:
            pass

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Cita.fecha_hora >= fecha_inicio_dt)
        except ValueError:
            pass

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Cita.fecha_hora <= fecha_fin_dt)
        except ValueError:
            pass

    citas = query.order_by(Cita.fecha_hora.desc()).all()

    citas_data = []

    for c in citas:
        cliente = db.session.query(Cliente).filter(Cliente.id_cliente == c.id_cliente).first()
        empleado = db.session.query(Empleado).filter(Empleado.id_empleado == c.id_empleado).first()

        detalle = db.session.query(DetalleCita).filter(
            DetalleCita.id_cita == c.id_cita
        ).first()

        nombre_item = obtener_nombre_servicio_o_promocion(detalle)
        estado_pago = obtener_estado_pago_cita(c.id_cita)

        citas_data.append({
            'id_cita': c.id_cita,
            'cliente': obtener_nombre_persona_por_cliente(cliente),
            'empleado': obtener_nombre_persona_por_empleado(empleado),
            'servicio': nombre_item,
            'fecha_hora': c.fecha_hora,
            'estatus': c.estatus,
            'estado_pago': estado_pago
        })

    return render_template(
        'citas/listado_citas.html',
        form=filtro_form,
        citas=citas_data,
        active_page='citas'
    )


@citas_bp.route('/citas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_cita():
    cita_form = forms.CitaForm()
    cargar_opciones_formulario_cita(cita_form)

    empleado_logueado = ajustar_formulario_para_empleado_logueado(cita_form)

    if not usuario_es_admin() and not empleado_logueado:
        flash('No se pudo identificar al empleado logueado', 'danger')
        return redirect(url_for('citas_bp.listado_citas'))

    if request.method == 'GET' and empleado_logueado:
        cita_form.id_empleado.data = empleado_logueado.id_empleado

    if cita_form.validate_on_submit():
        if not usuario_es_admin() and cita_form.id_empleado.data != empleado_logueado.id_empleado:
            flash('No tienes permiso para registrar citas a nombre de otro empleado', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        if cita_form.fecha_hora.data < datetime.now():
            flash('No se pueden agendar citas en fechas pasadas', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        hora = cita_form.fecha_hora.data.time()
        if not (time(9, 0) <= hora <= time(20, 0)):
            flash('La cita debe estar dentro del horario laboral (9:00 a 20:00)', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == cita_form.id_empleado.data,
            Cita.fecha_hora == cita_form.fecha_hora.data,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ese horario ya está ocupado para el empleado seleccionado', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        tipo_seleccion, id_seleccion = descomponer_seleccion_item(cita_form.id_servicio.data)

        if not tipo_seleccion or not id_seleccion:
            flash('Debes seleccionar un servicio o promoción válido', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        stock_ok, mensaje_stock = validar_stock_item(tipo_seleccion, id_seleccion)
        if not stock_ok:
            flash(f'No se puede registrar la cita porque no hay insumos suficientes. {mensaje_stock}', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        nueva_cita = Cita(
            fecha_hora=cita_form.fecha_hora.data,
            estatus=cita_form.estatus.data,
            id_cliente=cita_form.id_cliente.data,
            id_empleado=cita_form.id_empleado.data
        )

        try:
            db.session.add(nueva_cita)
            db.session.flush()

            item = obtener_item_servicio_o_promocion(tipo_seleccion, id_seleccion)

            if not item:
                db.session.rollback()
                flash('No se pudo obtener el servicio o promoción seleccionado', 'danger')
                return render_template(
                    'citas/cita_form.html',
                    form=cita_form,
                    active_page='citas'
                )

            detalle = DetalleCita(
                id_cita=nueva_cita.id_cita,
                id_servicio=item['id_servicio'],
                id_promocion=item['id_promocion'],
                subtotal=item['subtotal'],
                descuento=item['descuento']
            )
            db.session.add(detalle)
            db.session.flush()

            movimientos_generados = []
            if nueva_cita.estatus != 'CANCELADA':
                movimientos_generados = ejecutar_consumo_automatico(nueva_cita.id_cita)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_CITA",
                tabla="cita",
                registro_id=nueva_cita.id_cita,
                descripcion=(
                    f"Se registró la cita ID {nueva_cita.id_cita} "
                    f"para cliente {nueva_cita.id_cliente} "
                    f"con empleado {nueva_cita.id_empleado}"
                )
            )

            for mov in movimientos_generados:
                registrar_log(
                    session.get('user_id', 0),
                    "CONSUMO_AUTOMATICO",
                    tabla="movimiento_inventario",
                    registro_id=0,
                    descripcion=(
                        f"Consumo automático del producto {mov['codigo_producto']} "
                        f"por cantidad {mov['cantidad']} en cita {nueva_cita.id_cita}"
                    )
                )

            flash('Cita registrada correctamente', 'success')
            return redirect(url_for('citas_bp.listado_citas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar cita: {str(e)}', 'danger')

    return render_template(
        'citas/cita_form.html',
        form=cita_form,
        active_page='citas'
    )


@citas_bp.route('/citas/detalle', methods=['GET'])
@login_required
def detalle_cita():
    id_cita = request.args.get('id')
    cita = db.session.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita:
        flash('Cita no encontrada', 'danger')
        return redirect(url_for('citas_bp.listado_citas'))

    if not usuario_es_admin():
        empleado_logueado = obtener_empleado_logueado()

        if not empleado_logueado or cita.id_empleado != empleado_logueado.id_empleado:
            flash('No tienes permiso para ver esta cita', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

    cliente = db.session.query(Cliente).filter(Cliente.id_cliente == cita.id_cliente).first()
    empleado = db.session.query(Empleado).filter(Empleado.id_empleado == cita.id_empleado).first()

    detalles = db.session.query(DetalleCita).filter(
        DetalleCita.id_cita == cita.id_cita
    ).all()

    servicios_data = []
    for d in detalles:
        nombre_item = obtener_nombre_servicio_o_promocion(d)
        servicios_data.append({
            'nombre_servicio': nombre_item,
            'subtotal': d.subtotal,
            'descuento': d.descuento
        })

    estado_pago = obtener_estado_pago_cita(cita.id_cita)

    info_pago = {
        'estado_pago': estado_pago
    }

    return render_template(
        'citas/detalle_citas.html',
        cita=cita,
        cliente=obtener_nombre_persona_por_cliente(cliente),
        empleado=obtener_nombre_persona_por_empleado(empleado),
        servicios=servicios_data,
        estado_pago=estado_pago,
        info_pago=info_pago,
        active_page='citas'
    )


@citas_bp.route('/citas/editar', methods=['GET', 'POST'])
@login_required
def editar_cita():
    cita_form = forms.CitaForm()
    cargar_opciones_formulario_cita(cita_form)

    empleado_logueado = ajustar_formulario_para_empleado_logueado(cita_form)

    if request.method == 'GET':
        id_cita = request.args.get('id')
        cita = db.session.query(Cita).filter(Cita.id_cita == id_cita).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        if not usuario_es_admin():
            if not empleado_logueado or cita.id_empleado != empleado_logueado.id_empleado:
                flash('No tienes permiso para editar esta cita', 'danger')
                return redirect(url_for('citas_bp.listado_citas'))

        detalle = db.session.query(DetalleCita).filter(
            DetalleCita.id_cita == cita.id_cita
        ).first()

        cita_form.id.data = cita.id_cita
        cita_form.id_cliente.data = cita.id_cliente
        cita_form.id_empleado.data = cita.id_empleado
        cita_form.fecha_hora.data = cita.fecha_hora
        cita_form.estatus.data = cita.estatus

        if detalle:
            if detalle.id_servicio:
                cita_form.id_servicio.data = f"SERVICIO-{detalle.id_servicio}"
            elif detalle.id_promocion:
                cita_form.id_servicio.data = f"PROMOCION-{detalle.id_promocion}"

    if cita_form.validate_on_submit():
        cita = db.session.query(Cita).filter(Cita.id_cita == cita_form.id.data).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        if not usuario_es_admin():
            if not empleado_logueado or cita.id_empleado != empleado_logueado.id_empleado:
                flash('No tienes permiso para editar esta cita', 'danger')
                return redirect(url_for('citas_bp.listado_citas'))

            if cita_form.id_empleado.data != empleado_logueado.id_empleado:
                flash('No puedes reasignar la cita a otro empleado', 'danger')
                return redirect(url_for('citas_bp.listado_citas'))

        if cita_form.fecha_hora.data < datetime.now() and cita.estatus != 'FINALIZADA':
            flash('No se pueden agendar citas en fechas pasadas', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        hora = cita_form.fecha_hora.data.time()
        if not (time(9, 0) <= hora <= time(20, 0)):
            flash('La cita debe estar dentro del horario laboral (9:00 a 20:00)', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == cita_form.id_empleado.data,
            Cita.fecha_hora == cita_form.fecha_hora.data,
            Cita.id_cita != cita.id_cita,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ese horario ya está ocupado para el empleado seleccionado', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        detalle_actual = db.session.query(DetalleCita).filter(
            DetalleCita.id_cita == cita.id_cita
        ).first()

        tipo_actual = None
        id_actual = None
        if detalle_actual:
            if detalle_actual.id_servicio:
                tipo_actual = 'SERVICIO'
                id_actual = detalle_actual.id_servicio
            elif detalle_actual.id_promocion:
                tipo_actual = 'PROMOCION'
                id_actual = detalle_actual.id_promocion

        tipo_seleccion, id_seleccion = descomponer_seleccion_item(cita_form.id_servicio.data)

        if not tipo_seleccion or not id_seleccion:
            flash('Debes seleccionar un servicio o promoción válido', 'danger')
            return render_template(
                'citas/cita_form.html',
                form=cita_form,
                active_page='citas'
            )

        cambio_item = (tipo_actual != tipo_seleccion) or (id_actual != id_seleccion)
        cita_cancelada_antes = cita.estatus == 'CANCELADA'
        cita_cancelada_nueva = cita_form.estatus.data == 'CANCELADA'

        if cambio_item or cita_cancelada_antes:
            stock_ok, mensaje_stock = validar_stock_item(tipo_seleccion, id_seleccion)
            if not stock_ok and not cita_cancelada_nueva:
                flash(f'No se puede modificar la cita porque no hay insumos suficientes. {mensaje_stock}', 'danger')
                return render_template(
                    'citas/cita_form.html',
                    form=cita_form,
                    active_page='citas'
                )

        try:
            movimientos_revertidos = []
            movimientos_generados = []

            if cita.estatus != 'CANCELADA':
                movimientos_revertidos = revertir_consumo_automatico(cita.id_cita)

            cita.id_cliente = cita_form.id_cliente.data
            cita.id_empleado = cita_form.id_empleado.data
            cita.fecha_hora = cita_form.fecha_hora.data
            cita.estatus = cita_form.estatus.data

            db.session.query(DetalleCita).filter(
                DetalleCita.id_cita == cita.id_cita
            ).delete()

            item = obtener_item_servicio_o_promocion(tipo_seleccion, id_seleccion)

            if not item:
                db.session.rollback()
                flash('No se pudo obtener el servicio o promoción seleccionado', 'danger')
                return render_template(
                    'citas/cita_form.html',
                    form=cita_form,
                    active_page='citas'
                )

            detalle = DetalleCita(
                id_cita=cita.id_cita,
                id_servicio=item['id_servicio'],
                id_promocion=item['id_promocion'],
                subtotal=item['subtotal'],
                descuento=item['descuento']
            )
            db.session.add(detalle)
            db.session.flush()

            if cita.estatus != 'CANCELADA':
                movimientos_generados = ejecutar_consumo_automatico(cita.id_cita)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_CITA",
                tabla="cita",
                registro_id=cita.id_cita,
                descripcion=f"Se modificó la cita ID {cita.id_cita}. Nuevo estatus: {cita.estatus}"
            )

            for mov in movimientos_revertidos:
                registrar_log(
                    session.get('user_id', 0),
                    "REVERSION_CONSUMO",
                    tabla="movimiento_inventario",
                    registro_id=0,
                    descripcion=(
                        f"Se devolvió al inventario el producto {mov['codigo_producto']} "
                        f"por cantidad {mov['cantidad']} al editar la cita {cita.id_cita}"
                    )
                )

            for mov in movimientos_generados:
                registrar_log(
                    session.get('user_id', 0),
                    "CONSUMO_AUTOMATICO",
                    tabla="movimiento_inventario",
                    registro_id=0,
                    descripcion=(
                        f"Consumo automático del producto {mov['codigo_producto']} "
                        f"por cantidad {mov['cantidad']} en cita {cita.id_cita}"
                    )
                )

            flash('Cita modificada correctamente', 'success')
            return redirect(url_for('citas_bp.listado_citas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar cita: {str(e)}', 'danger')

    return render_template(
        'citas/cita_form.html',
        form=cita_form,
        active_page='citas'
    )


@citas_bp.route('/citas/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_cita():
    cita_form = forms.CitaForm()
    cargar_opciones_formulario_cita(cita_form)

    empleado_logueado = ajustar_formulario_para_empleado_logueado(cita_form)

    if request.method == 'GET':
        id_cita = request.args.get('id')
        cita = db.session.query(Cita).filter(Cita.id_cita == id_cita).first()

        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

        if not usuario_es_admin():
            if not empleado_logueado or cita.id_empleado != empleado_logueado.id_empleado:
                flash('No tienes permiso para cancelar esta cita', 'danger')
                return redirect(url_for('citas_bp.listado_citas'))

        detalle = db.session.query(DetalleCita).filter(
            DetalleCita.id_cita == cita.id_cita
        ).first()

        cita_form.id.data = cita.id_cita
        cita_form.id_cliente.data = cita.id_cliente
        cita_form.id_empleado.data = cita.id_empleado
        cita_form.fecha_hora.data = cita.fecha_hora
        cita_form.estatus.data = cita.estatus

        if detalle:
            if detalle.id_servicio:
                cita_form.id_servicio.data = f"SERVICIO-{detalle.id_servicio}"
            elif detalle.id_promocion:
                cita_form.id_servicio.data = f"PROMOCION-{detalle.id_promocion}"

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

    if not usuario_es_admin():
        if not empleado_logueado or cita.id_empleado != empleado_logueado.id_empleado:
            flash('No tienes permiso para cancelar esta cita', 'danger')
            return redirect(url_for('citas_bp.listado_citas'))

    try:
        movimientos_revertidos = []

        if cita.estatus != 'CANCELADA':
            movimientos_revertidos = revertir_consumo_automatico(cita.id_cita)

        cita.estatus = 'CANCELADA'
        db.session.commit()

        registrar_log(
            session.get('user_id', 0),
            "CANCELACION_CITA",
            tabla="cita",
            registro_id=cita.id_cita,
            descripcion=f"Se canceló la cita ID {cita.id_cita}"
        )

        for mov in movimientos_revertidos:
            registrar_log(
                session.get('user_id', 0),
                "REVERSION_CONSUMO",
                tabla="movimiento_inventario",
                registro_id=0,
                descripcion=(
                    f"Se devolvió al inventario el producto {mov['codigo_producto']} "
                    f"por cantidad {mov['cantidad']} al cancelar la cita {cita.id_cita}"
                )
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
    cliente_actual = obtener_cliente_logueado()

    if not cliente_actual:
        flash('Debes completar tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))

    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()
    empleados = Empleado.query.join(Puesto).filter(
    Empleado.estatus == 'ACTIVO',
    Puesto.nombre_puesto.in_(['MANICURISTA', 'PEDICURISTA'])).all()
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        id_servicio = request.form.get('id_servicio')
        id_empleado = request.form.get('id_empleado')
        notas = request.form.get('notas', '')

        if not fecha or not hora or not id_servicio or not id_empleado:
            flash('Todos los campos son requeridos', 'danger')
            return redirect(url_for('citas_bp.agendar_cita'))

        try:
            fecha_hora_cita = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')

            if fecha_hora_cita < datetime.now():
                flash('No se pueden agendar citas en fechas u horarios pasados', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            hora_cita = fecha_hora_cita.time()
            if not (time(9, 0) <= hora_cita <= time(20, 0)):
                flash('La cita debe estar dentro del horario laboral (9:00 a 20:00 hrs)', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            servicio = Servicio.query.filter(
                Servicio.id_servicio == int(id_servicio),
                Servicio.estatus == 'ACTIVO'
            ).first()

            if not servicio:
                flash('El servicio seleccionado no disponible', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            empleado = Empleado.query.filter(
                Empleado.id_empleado == int(id_empleado),
                Empleado.estatus == 'ACTIVO'
            ).first()

            if not empleado:
                flash('El empleado seleccionado no disponible', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            cita_existente = db.session.query(Cita).filter(
                Cita.id_empleado == int(id_empleado),
                Cita.fecha_hora == fecha_hora_cita,
                Cita.estatus != 'CANCELADA'
            ).first()

            if cita_existente:
                flash('El empleado seleccionado ya tiene una cita agendada en ese horario', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            # Validación mejorada de stock
            stock_ok, mensaje_stock = validar_stock_servicio(servicio.id_servicio)
            
            if not stock_ok:
                # Mostrar mensaje detallado de qué productos faltan
                flash(f'No es posible agendar la cita por este momento.', 'danger')
                return redirect(url_for('citas_bp.agendar_cita'))

            # Verificar si hay stock suficiente (mensaje de advertencia pero permitir agendar)
            insumos_bajos = []
            insumos_servicio = db.session.query(InsumoServicio).filter(
                InsumoServicio.id_servicio == servicio.id_servicio
            ).all()
            
            for insumo in insumos_servicio:
                producto = db.session.query(Producto).filter(
                    Producto.codigo_producto == insumo.codigo_producto
                ).first()
                
                if producto:
                    stock_actual = Decimal(str(producto.stock_actual if producto.stock_actual is not None else 0))
                    cantidad_requerida = Decimal(str(insumo.cantidad_utilizada if insumo.cantidad_utilizada is not None else 0))
                    
                    # Si el stock está por debajo del 20% de lo requerido para 5 citas
                    if stock_actual < (cantidad_requerida * 5):
                        insumos_bajos.append(f"{producto.nombre} (stock: {stock_actual})")
            
            # Crear la cita
            nueva_cita = Cita(
                fecha_hora=fecha_hora_cita,
                estatus='PENDIENTE',
                id_cliente=cliente_actual.id_cliente,
                id_empleado=int(id_empleado)
            )

            db.session.add(nueva_cita)
            db.session.flush()

            detalle = DetalleCita(
                id_cita=nueva_cita.id_cita,
                id_servicio=servicio.id_servicio,
                id_promocion=None,
                subtotal=servicio.precio,
                descuento=0
            )
            db.session.add(detalle)

            db.session.commit()

            # Registrar log de la cita
            registrar_log(
                current_user.id_usuario,
                "AGENDAR_CITA",
                tabla="cita",
                registro_id=nueva_cita.id_cita,
                descripcion=f"Cita #{nueva_cita.id_cita} agendada para {fecha_hora_cita.strftime('%d/%m/%Y %H:%M')} con empleado {empleado.id_empleado} para servicio {servicio.nombre_servicio}"
            )

            # Mensaje de éxito
            mensaje_exito = f'Cita agendada exitosamente para {fecha_hora_cita.strftime("%d/%m/%Y %H:%M")}'
            
            if insumos_bajos:
                mensaje_exito += f'\n\n Advertencia: Algunos productos tienen stock bajo:\n- ' + '\n- '.join(insumos_bajos)
                mensaje_exito += '\n\nTe recomendamos contactar al establecimiento para confirmar disponibilidad.'
                flash(mensaje_exito, 'warning')
            else:
                flash(mensaje_exito, 'success')
                
            return redirect(url_for('citas_bp.mis_citas_cliente'))

        except Exception as e:
            db.session.rollback()
            print(f"ERROR al agendar cita: {str(e)}")
            flash(f'Error al agendar la cita: {str(e)}', 'danger')
            return redirect(url_for('citas_bp.agendar_cita'))

    return render_template(
        'vistaClientes/citas/agendar_cita.html',
        cliente_actual=cliente_actual,
        servicios=servicios,
        empleados=empleados,
        datetime=datetime
    )
@citas_bp.route('/citas/mis-citas')
@login_required
def mis_citas_cliente():
    cliente = obtener_cliente_logueado()

    if not cliente:
        flash('No se encontró tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))

    citas = Cita.query.filter_by(id_cliente=cliente.id_cliente).order_by(Cita.fecha_hora.desc()).all()

    citas_data = []

    for cita in citas:
        detalles = DetalleCita.query.filter_by(id_cita=cita.id_cita).all()

        if len(detalles) == 1:
            servicio_nombre = obtener_nombre_servicio_o_promocion(detalles[0])
        elif len(detalles) > 1:
            servicio_nombre = "Múltiples"
        else:
            servicio_nombre = "Sin detalle"

        total = float(obtener_total_cita(cita.id_cita))
        estado_pago = obtener_estado_pago_cita(cita.id_cita)

        citas_data.append({
            'id_cita': cita.id_cita,
            'fecha_hora': cita.fecha_hora,
            'estatus': cita.estatus,
            'servicio_nombre': servicio_nombre,
            'total': total,
            'estado_pago': estado_pago
        })

    return render_template('vistaClientes/citas/mis_citas_cliente.html', citas=citas_data)


@citas_bp.route('/citas/detalle-cliente')
@login_required
def detalle_cita_cliente():
    id_cita = request.args.get('id')
    cita = Cita.query.get_or_404(id_cita)

    cliente = obtener_cliente_logueado()

    if not cliente:
        flash('No se encontró tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))

    if cita.id_cliente != cliente.id_cliente:
        flash('No tienes permiso para ver esta cita', 'danger')
        return redirect(url_for('citas_bp.mis_citas_cliente'))

    detalles_bd = DetalleCita.query.filter_by(id_cita=cita.id_cita).all()
    detalles = []

    for detalle in detalles_bd:
        nombre_item = obtener_nombre_servicio_o_promocion(detalle)
        precio_item = detalle.subtotal if detalle.subtotal is not None else 0
        detalles.append((detalle, nombre_item, precio_item))

    pago = Pago.query.filter_by(id_cita=cita.id_cita).first()
    total = obtener_total_cita(cita.id_cita)

    # Obtener nombre del empleado
    empleado_nombre = None
    if cita.id_empleado:
        empleado = Empleado.query.get(cita.id_empleado)
        if empleado and empleado.persona:
            empleado_nombre = f"{empleado.persona.nombre_persona} {empleado.persona.apellidos}"

    return render_template(
        'vistaClientes/citas/detalle_cita_cliente.html',
        cita=cita,
        detalles=detalles,
        pago=pago,
        total=total,
        empleado_nombre=empleado_nombre  # <-- Pasar nombre del empleado al template
    )


@citas_bp.route('/citas/cancelar-cliente/<int:id>', methods=['GET', 'POST'])
@login_required
def cancelar_cita_cliente(id):
    cita = Cita.query.get_or_404(id)
    cliente = obtener_cliente_logueado()

    if not cliente:
        flash('No se encontró tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))

    if cita.id_cliente != cliente.id_cliente:
        flash('No tienes permiso para cancelar esta cita', 'danger')
        return redirect(url_for('citas_bp.mis_citas_cliente'))

    if cita.estatus in ['PENDIENTE', 'CONFIRMADA']:
        cita.estatus = 'CANCELADA'
        db.session.commit()

        registrar_log(
            current_user.id_usuario,
            'CANCELAR_CITA',
            tabla='cita',
            registro_id=id,
            descripcion=f'Cita #{id} cancelada por el cliente'
        )

        flash('Cita cancelada exitosamente', 'success')
    else:
        flash(f'No se puede cancelar esta cita porque ya está {cita.estatus.lower()}', 'warning')

    return redirect(url_for('citas_bp.mis_citas_cliente'))