from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Cita, Cliente, Empleado, Persona, DetalleCita, Servicio, Pago, registrar_log
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from . import agenda_bp


@agenda_bp.route('/test')
def test():
    return "¡El blueprint de agenda funciona correctamente!"


@agenda_bp.route('/agenda')
@login_required
def agenda():
    """Vista de agenda para administradores/empleados"""
    query = db.session.query(
        Cita.id_cita,
        Cita.fecha_hora,
        Cita.estatus,
        Persona.nombre_persona.label('cliente_nombre'),
        Persona.apellidos.label('cliente_apellidos')
    ).join(Cliente, Cita.id_cliente == Cliente.id_cliente)\
     .join(Persona, Cliente.id_persona == Persona.id_persona)
    
    # Filtros
    estatus = request.args.get('estatus')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    buscar = request.args.get('buscar')
    
    if estatus:
        query = query.filter(Cita.estatus == estatus)
    
    if fecha_inicio:
        query = query.filter(Cita.fecha_hora >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    
    if fecha_fin:
        query = query.filter(Cita.fecha_hora <= datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1))
    
    if buscar:
        query = query.filter(
            or_(
                Persona.nombre_persona.like(f'%{buscar}%'),
                Persona.apellidos.like(f'%{buscar}%')
            )
        )
    
    citas = query.order_by(Cita.fecha_hora.desc()).all()
    
    # Procesar datos para la plantilla
    citas_data = []
    for cita in citas:
        servicios_count = DetalleCita.query.filter_by(id_cita=cita.id_cita).count()
        total = db.session.query(func.sum(DetalleCita.subtotal)).filter_by(id_cita=cita.id_cita).scalar() or 0
        
        empleado_info = db.session.query(
            Persona.nombre_persona, Persona.apellidos
        ).join(Empleado, Persona.id_persona == Empleado.id_persona)\
         .join(Cita, Empleado.id_empleado == Cita.id_empleado)\
         .filter(Cita.id_cita == cita.id_cita).first()
        
        empleado_nombre = f"{empleado_info[0]} {empleado_info[1]}" if empleado_info else 'No asignado'
        
        citas_data.append({
            'id_cita': cita.id_cita,
            'fecha_hora': cita.fecha_hora,
            'estatus': cita.estatus,
            'cliente_nombre': f"{cita.cliente_nombre} {cita.cliente_apellidos}",
            'empleado_nombre': empleado_nombre,
            'servicios_count': servicios_count,
            'total': float(total)
        })
    
    return render_template('vistaClientes/citas/citas.html', citas=citas_data)


@agenda_bp.route('/mis-citas')
@login_required
def mis_citas():
    """Vista de citas para clientes"""
    cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if not cliente:
        flash('No se encontró tu perfil de cliente', 'warning')
        return redirect(url_for('acceso.dashboard'))
    
    citas = Cita.query.filter_by(id_cliente=cliente.id_cliente).order_by(Cita.fecha_hora.desc()).all()
    
    citas_data = []
    for cita in citas:
        servicios_count = DetalleCita.query.filter_by(id_cita=cita.id_cita).count()
        total = db.session.query(func.sum(DetalleCita.subtotal)).filter_by(id_cita=cita.id_cita).scalar() or 0
        
        empleado_info = db.session.query(
            Persona.nombre_persona, Persona.apellidos
        ).join(Empleado, Persona.id_persona == Empleado.id_persona)\
         .filter(Empleado.id_empleado == cita.id_empleado).first()
        
        empleado_nombre = f"{empleado_info[0]} {empleado_info[1]}" if empleado_info else 'No asignado'
        
        citas_data.append({
            'id_cita': cita.id_cita,
            'fecha_hora': cita.fecha_hora,
            'estatus': cita.estatus,
            'empleado_nombre': empleado_nombre,
            'servicios_count': servicios_count,
            'total': float(total)
        })
    
    return render_template('vistaClientes/citas/mis_citas.html', citas=citas_data)


@agenda_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    cita = Cita.query.get_or_404(id)
    
    # Obtener detalles con nombres de servicios
    detalles = db.session.query(
        DetalleCita,
        Servicio.nombre_servicio,
        Servicio.precio
    ).join(Servicio, DetalleCita.id_servicio == Servicio.id_servicio)\
     .filter(DetalleCita.id_cita == id).all()
    
    pago = Pago.query.filter_by(id_cita=id).first()
    
    # Obtener información del cliente y empleado
    cliente = Cliente.query.get(cita.id_cliente)
    empleado = Empleado.query.get(cita.id_empleado)
    
    cliente_nombre = f"{cliente.persona.nombre_persona} {cliente.persona.apellidos}" if cliente else 'N/A'
    empleado_nombre = f"{empleado.persona.nombre_persona} {empleado.persona.apellidos}" if empleado else 'No asignado'
    
    return render_template('vistaClientes/citas/ver.html',
                          cita=cita, 
                          detalles=detalles, 
                          pago=pago,
                          cliente_nombre=cliente_nombre,
                          empleado_nombre=empleado_nombre)


@agenda_bp.route('/confirmar/<int:id>')
@login_required
def confirmar(id):
    cita = Cita.query.get_or_404(id)
    
    if cita.estatus == 'PENDIENTE':
        cita.estatus = 'CONFIRMADA'
        db.session.commit()
        registrar_log(current_user.id_usuario, 'CONFIRMAR', 'citas', f'Cita #{id} confirmada')
        flash('Cita confirmada exitosamente', 'success')
    else:
        flash('No se puede confirmar esta cita', 'warning')
    
    return redirect(url_for('citas.agenda'))


@agenda_bp.route('/cancelar/<int:id>')
@login_required
def cancelar(id):
    cita = Cita.query.get_or_404(id)
    
    if cita.estatus in ['PENDIENTE', 'CONFIRMADA']:
        cita.estatus = 'CANCELADA'
        db.session.commit()
        registrar_log(current_user.id_usuario, 'CANCELAR', 'citas', f'Cita #{id} cancelada')
        flash('Cita cancelada exitosamente', 'success')
    else:
        flash('No se puede cancelar esta cita', 'warning')
    
    return redirect(request.referrer or url_for('citas.agenda'))


@agenda_bp.route('/finalizar/<int:id>')
@login_required
def finalizar(id):
    cita = Cita.query.get_or_404(id)
    
    if cita.estatus == 'CONFIRMADA':
        cita.estatus = 'FINALIZADA'
        
        total = db.session.query(func.sum(DetalleCita.subtotal)).filter_by(id_cita=id).scalar() or 0
        
        pago = Pago(
            fecha_pago=datetime.now(),
            subtotal=total,
            impuesto=0,
            propina=0,
            total=total,
            id_cita=id
        )
        db.session.add(pago)
        db.session.commit()
        
        registrar_log(current_user.id_usuario, 'FINALIZAR', 'citas', f'Cita #{id} finalizada. Total: ${total}')
        flash(f'Cita finalizada exitosamente. Total: ${total}', 'success')
    else:
        flash('No se puede finalizar esta cita', 'warning')
    
    return redirect(url_for('citas.agenda'))