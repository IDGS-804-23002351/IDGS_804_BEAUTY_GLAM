from flask import render_template, redirect, url_for, flash
from . import cliente_servicios_bp
from models import db, Servicio
from flask_login import login_required


@cliente_servicios_bp.route('/cliente/servicios', methods=['GET'])
@login_required
def listado_servicios_cliente():
    servicios = db.session.query(Servicio).filter(
        Servicio.estatus == 'ACTIVO'
    ).order_by(Servicio.nombre_servicio.asc()).all()

    return render_template(
        'vistaClientes/clientes_servicios/listado_servicios_cliente.html',
        servicios=servicios,
        active_page='servicios_ cliente'
    )


@cliente_servicios_bp.route('/cliente/servicios/<int:id_servicio>', methods=['GET'])
@login_required
def detalle_servicio_cliente(id_servicio):
    servicio = db.session.query(Servicio).filter(
        Servicio.id_servicio == id_servicio,
        Servicio.estatus == 'ACTIVO'
    ).first()

    if not servicio:
        flash('Servicio no encontrado')
        return redirect(url_for('cliente_servicios_bp.listado_servicios_cliente'))

    return render_template(
        'vistaClientes/clientes_servicios/detalle_servicio_cliente.html',
        servicio=servicio,
        active_page='servicios_cliente'
    )