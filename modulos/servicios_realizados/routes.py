from flask import render_template, request, redirect, url_for, flash, session
from decimal import Decimal
from sqlalchemy.orm import aliased

from . import servicios_realizados_bp
import forms
from models import db
from models import (
    Cita, DetalleCita, Servicio, Cliente, Empleado, Persona,
    registrar_log
)


@servicios_realizados_bp.route('/servicios-realizados', methods=['GET', 'POST'])
def listado_servicios_realizados():
    filtro_form = forms.FiltroServicioRealizadoForm()

    clientes = (
        db.session.query(Cliente, Persona)
        .join(Persona, Cliente.id_persona == Persona.id_persona)
        .all()
    )

    empleados = (
        db.session.query(Empleado, Persona)
        .join(Persona, Empleado.id_persona == Persona.id_persona)
        .all()
    )

    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    filtro_form.id_cliente.choices = [(0, 'Todos')] + [
        (c.id_cliente, f"{p.nombre_persona} {p.apellidos}")
        for c, p in clientes
    ]

    filtro_form.id_empleado.choices = [(0, 'Todos')] + [
        (e.id_empleado, f"{p.nombre_persona} {p.apellidos}")
        for e, p in empleados
    ]

    filtro_form.id_servicio.choices = [(0, 'Todos')] + [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    PersonaCliente = aliased(Persona)
    PersonaEmpleado = aliased(Persona)

    query = (
        db.session.query(
            DetalleCita,
            Cita,
            Servicio,
            Cliente,
            Empleado,
            PersonaCliente,
            PersonaEmpleado
        )
        .join(Cita, DetalleCita.id_cita == Cita.id_cita)
        .join(Servicio, DetalleCita.id_servicio == Servicio.id_servicio)
        .join(Cliente, Cita.id_cliente == Cliente.id_cliente)
        .join(PersonaCliente, Cliente.id_persona == PersonaCliente.id_persona)
        .join(Empleado, Cita.id_empleado == Empleado.id_empleado)
        .join(PersonaEmpleado, Empleado.id_persona == PersonaEmpleado.id_persona)
        .filter(Cita.estatus == 'FINALIZADA')
    )

    id_cliente = request.args.get('id_cliente', '0')
    id_empleado = request.args.get('id_empleado', '0')
    id_servicio = request.args.get('id_servicio', '0')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')

    if id_cliente != '0':
        query = query.filter(Cita.id_cliente == int(id_cliente))

    if id_empleado != '0':
        query = query.filter(Cita.id_empleado == int(id_empleado))

    if id_servicio != '0':
        query = query.filter(DetalleCita.id_servicio == int(id_servicio))

    if fecha_inicio:
        query = query.filter(Cita.fecha_hora >= fecha_inicio.replace('T', ' '))

    if fecha_fin:
        query = query.filter(Cita.fecha_hora <= fecha_fin.replace('T', ' '))

    resultados = query.order_by(Cita.fecha_hora.desc()).all()

    registros = []
    for detalle, cita, servicio, cliente, empleado, persona_cliente, persona_empleado in resultados:
        registros.append({
            'id_cita': cita.id_cita,
            'id_detalle_cita': detalle.id_detalle_cita,
            'cliente': f"{persona_cliente.nombre_persona} {persona_cliente.apellidos}",
            'empleado': f"{persona_empleado.nombre_persona} {persona_empleado.apellidos}",
            'servicio': servicio.nombre_servicio,
            'fecha_hora': cita.fecha_hora,
            'subtotal': detalle.subtotal,
            'descuento': detalle.descuento,
            'estatus': cita.estatus
        })

    return render_template(
        'productos/listado_servicios_realizados.html',
        form=filtro_form,
        registros=registros,
        active_page='servicios_realizados'
    )


@servicios_realizados_bp.route('/servicios-realizados/nuevo', methods=['GET', 'POST'])
def nuevo_servicio_realizado():
    create_form = forms.ServicioRealizadoForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    create_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    create_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    create_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    if create_form.validate_on_submit():
        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == create_form.id_empleado.data,
            Cita.fecha_hora == create_form.fecha_hora.data,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ya existe una cita en ese horario para el empleado seleccionado', 'danger')
            return render_template(
                'productos/servicio_realizado_form.html',
                form=create_form,
                active_page='servicios_realizados'
            )

        try:
            nueva_cita = Cita(
                fecha_hora=create_form.fecha_hora.data,
                estatus=create_form.estatus.data,
                id_cliente=create_form.id_cliente.data,
                id_empleado=create_form.id_empleado.data
            )
            db.session.add(nueva_cita)
            db.session.flush()

            servicio = db.session.query(Servicio).filter(
                Servicio.id_servicio == create_form.id_servicio.data
            ).first()

            if not servicio:
                db.session.rollback()
                flash('Servicio no encontrado', 'danger')
                return render_template(
                    'productos/servicio_realizado_form.html',
                    form=create_form,
                    active_page='servicios_realizados'
                )

            descuento = create_form.descuento.data if create_form.descuento.data else Decimal('0.00')
            subtotal = Decimal(str(servicio.precio)) - Decimal(str(descuento))

            if subtotal < 0:
                subtotal = Decimal('0.00')

            detalle = DetalleCita(
                id_cita=nueva_cita.id_cita,
                id_servicio=servicio.id_servicio,
                subtotal=subtotal,
                descuento=descuento
            )
            db.session.add(detalle)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_SERVICIO_REALIZADO",
                tabla="detalle_cita",
                registro_id=detalle.id_detalle_cita,
                descripcion=f"Se registró el servicio realizado para la cita ID {nueva_cita.id_cita}"
            )

            if nueva_cita.estatus == 'FINALIZADA':
                registrar_log(
                    session.get('user_id', 0),
                    "FINALIZACION_CITA",
                    tabla="cita",
                    registro_id=nueva_cita.id_cita,
                    descripcion=f"Se registró una cita ya finalizada con ID {nueva_cita.id_cita}"
                )

            flash('Servicio realizado registrado correctamente', 'success')
            return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar servicio realizado: {str(e)}', 'danger')

    return render_template(
        'productos/servicio_realizado_form.html',
        form=create_form,
        active_page='servicios_realizados'
    )


@servicios_realizados_bp.route('/servicios-realizados/detalle', methods=['GET'])
def detalle_servicio_realizado():
    id_detalle = request.args.get('id')

    PersonaCliente = aliased(Persona)
    PersonaEmpleado = aliased(Persona)

    resultado = (
        db.session.query(
            DetalleCita,
            Cita,
            Servicio,
            PersonaCliente,
            PersonaEmpleado
        )
        .join(Cita, DetalleCita.id_cita == Cita.id_cita)
        .join(Servicio, DetalleCita.id_servicio == Servicio.id_servicio)
        .join(Cliente, Cita.id_cliente == Cliente.id_cliente)
        .join(PersonaCliente, Cliente.id_persona == PersonaCliente.id_persona)
        .join(Empleado, Cita.id_empleado == Empleado.id_empleado)
        .join(PersonaEmpleado, Empleado.id_persona == PersonaEmpleado.id_persona)
        .filter(DetalleCita.id_detalle_cita == id_detalle)
        .first()
    )

    if not resultado:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

    detalle, cita, servicio, persona_cliente, persona_empleado = resultado

    return render_template(
        'productos/detalle_servicio_realizado.html',
        cita=cita,
        detalle=detalle,
        servicio=servicio,
        cliente=f"{persona_cliente.nombre_persona} {persona_cliente.apellidos}",
        empleado=f"{persona_empleado.nombre_persona} {persona_empleado.apellidos}",
        active_page='servicios_realizados'
    )


@servicios_realizados_bp.route('/servicios-realizados/editar', methods=['GET', 'POST'])
def editar_servicio_realizado():
    create_form = forms.ServicioRealizadoForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    create_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    create_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    create_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    if request.method == 'GET':
        id = request.args.get('id')
        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_detalle_cita == id).first()

        if not detalle:
            flash('Registro no encontrado', 'danger')
            return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

        cita = db.session.query(Cita).filter(Cita.id_cita == detalle.id_cita).first()

        create_form.id_cita.data = cita.id_cita
        create_form.id_detalle_cita.data = detalle.id_detalle_cita
        create_form.id_cliente.data = cita.id_cliente
        create_form.id_empleado.data = cita.id_empleado
        create_form.id_servicio.data = detalle.id_servicio
        create_form.fecha_hora.data = cita.fecha_hora
        create_form.descuento.data = detalle.descuento
        create_form.estatus.data = cita.estatus

    if create_form.validate_on_submit():
        cita = db.session.query(Cita).filter(Cita.id_cita == create_form.id_cita.data).first()
        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_detalle_cita == create_form.id_detalle_cita.data).first()

        if not cita or not detalle:
            flash('Registro no encontrado', 'danger')
            return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

        cita_existente = db.session.query(Cita).filter(
            Cita.id_empleado == create_form.id_empleado.data,
            Cita.fecha_hora == create_form.fecha_hora.data,
            Cita.id_cita != cita.id_cita,
            Cita.estatus != 'CANCELADA'
        ).first()

        if cita_existente:
            flash('Ya existe una cita en ese horario para el empleado seleccionado', 'danger')
            return render_template(
                'productos/servicio_realizado_form.html',
                form=create_form,
                active_page='servicios_realizados'
            )

        servicio = db.session.query(Servicio).filter(
            Servicio.id_servicio == create_form.id_servicio.data
        ).first()

        if not servicio:
            flash('Servicio no encontrado', 'danger')
            return render_template(
                'productos/servicio_realizado_form.html',
                form=create_form,
                active_page='servicios_realizados'
            )

        descuento = create_form.descuento.data if create_form.descuento.data else Decimal('0.00')
        subtotal = Decimal(str(servicio.precio)) - Decimal(str(descuento))

        if subtotal < 0:
            subtotal = Decimal('0.00')

        estatus_anterior = cita.estatus

        try:
            cita.id_cliente = create_form.id_cliente.data
            cita.id_empleado = create_form.id_empleado.data
            cita.fecha_hora = create_form.fecha_hora.data
            cita.estatus = create_form.estatus.data

            detalle.id_servicio = create_form.id_servicio.data
            detalle.descuento = descuento
            detalle.subtotal = subtotal

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_SERVICIO_REALIZADO",
                tabla="detalle_cita",
                registro_id=detalle.id_detalle_cita,
                descripcion=f"Se modificó el servicio realizado de la cita ID {cita.id_cita}"
            )

            if estatus_anterior != 'FINALIZADA' and cita.estatus == 'FINALIZADA':
                registrar_log(
                    session.get('user_id', 0),
                    "FINALIZACION_CITA",
                    tabla="cita",
                    registro_id=cita.id_cita,
                    descripcion=f"Se finalizó la cita ID {cita.id_cita} desde servicios realizados"
                )

            flash('Servicio realizado modificado correctamente', 'success')
            return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar servicio realizado: {str(e)}', 'danger')

    return render_template(
        'productos/servicio_realizado_form.html',
        form=create_form,
        active_page='servicios_realizados'
    )


@servicios_realizados_bp.route('/servicios-realizados/eliminar', methods=['GET', 'POST'])
def eliminar_servicio_realizado():
    create_form = forms.ServicioRealizadoForm()

    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    servicios = Servicio.query.filter(Servicio.estatus == 'ACTIVO').all()

    create_form.id_cliente.choices = [
        (
            c.id_cliente,
            f"{c.persona.nombre_persona} {c.persona.apellidos}" if c.persona else f"Cliente {c.id_cliente}"
        )
        for c in clientes
    ]

    create_form.id_empleado.choices = [
        (
            e.id_empleado,
            f"{e.persona.nombre_persona} {e.persona.apellidos}" if e.persona else f"Empleado {e.id_empleado}"
        )
        for e in empleados
    ]

    create_form.id_servicio.choices = [
        (s.id_servicio, s.nombre_servicio)
        for s in servicios
    ]

    cita = None
    detalle = None

    if request.method == 'GET':
        id = request.args.get('id')
        detalle = db.session.query(DetalleCita).filter(DetalleCita.id_detalle_cita == id).first()

        if not detalle:
            flash('Registro no encontrado', 'danger')
            return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

        cita = db.session.query(Cita).filter(Cita.id_cita == detalle.id_cita).first()

        create_form.id_cita.data = cita.id_cita
        create_form.id_detalle_cita.data = detalle.id_detalle_cita
        create_form.id_cliente.data = cita.id_cliente
        create_form.id_empleado.data = cita.id_empleado
        create_form.id_servicio.data = detalle.id_servicio
        create_form.fecha_hora.data = cita.fecha_hora
        create_form.descuento.data = detalle.descuento
        create_form.estatus.data = cita.estatus

        return render_template(
            'productos/eliminar_servicio_realizado.html',
            form=create_form,
            cita=cita,
            detalle=detalle,
            active_page='servicios_realizados'
        )

    id_cita = request.form.get('id_cita')
    cita = db.session.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

    try:
        cita.estatus = 'CANCELADA'
        db.session.commit()

        registrar_log(
            session.get('user_id', 0),
            "BAJA_SERVICIO_REALIZADO",
            tabla="cita",
            registro_id=cita.id_cita,
            descripcion=f"Se canceló el servicio realizado de la cita ID {cita.id_cita}"
        )

        flash('Servicio realizado eliminado correctamente', 'warning')
        return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar servicio realizado: {str(e)}', 'danger')
        return redirect(url_for('servicios_realizados_bp.listado_servicios_realizados'))