from flask import render_template, request, redirect, url_for, flash
from . import proceso_pago
from models import db
from sqlalchemy import text
from flask_login import login_required
from datetime import datetime

@proceso_pago.route('/pagos', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('search', '')
    metodo_sel = request.args.get('metodo', '')
    fecha_sel = request.args.get('fecha', '')

    query_text = """
        SELECT 
            c.id_cita,
            CASE 
                WHEN p.id_pago IS NOT NULL THEN CONCAT('BG-', p.id_pago)
                ELSE 'PENDIENTE'
            END AS folio,
            CONCAT(per.nombre_persona, ' ', per.apellidos) AS cliente,
            GROUP_CONCAT(s.nombre_servicio SEPARATOR ', ') AS servicio,
            COALESCE(SUM(
                (dc.subtotal - (dc.subtotal * COALESCE(pr.valor_descuento, 0) / 100)) * 1.16
            ), 0) AS total,
            COALESCE(mp.nombre_metodo, 'N/A') AS metodo,
            COALESCE(DATE(p.fecha_pago), DATE(c.fecha_hora)) AS fecha,
            c.estatus AS cita_estatus,
            p.id_pago
        FROM cita c
        INNER JOIN cliente cl ON c.id_cliente = cl.id_cliente
        INNER JOIN persona per ON cl.id_persona = per.id_persona
        LEFT JOIN detalle_cita dc ON c.id_cita = dc.id_cita
        LEFT JOIN servicio s ON dc.id_servicio = s.id_servicio
        LEFT JOIN promocion pr ON s.nombre_servicio = pr.tipo_promocion
        LEFT JOIN pago p ON c.id_cita = p.id_cita
        LEFT JOIN metodo_pago mp ON p.id_metodo_pago = mp.id_metodo_pago
        WHERE c.estatus = 'FINALIZADA'
    """
    
    params = {}
    if search_query:
        query_text += " AND (per.nombre_persona LIKE :search OR per.apellidos LIKE :search)"
        params['search'] = f"%{search_query}%"
    
    if metodo_sel:
        query_text += " AND mp.id_metodo_pago = :metodo"
        params['metodo'] = metodo_sel

    if fecha_sel:
        query_text += " AND DATE(COALESCE(p.fecha_pago, c.fecha_hora)) = :fecha"
        params['fecha'] = fecha_sel

    query_text += " GROUP BY c.id_cita, p.id_pago, mp.nombre_metodo"
    query_text += " ORDER BY COALESCE(p.fecha_pago, c.fecha_hora) DESC"

    pagos = db.session.execute(text(query_text), params).fetchall()
    metodos = db.session.execute(text("SELECT id_metodo_pago, nombre_metodo FROM metodo_pago")).fetchall()

    return render_template(
        'pagos/pagos.html', 
        pagos=pagos, 
        metodos=metodos,
        busqueda=search_query,
        fecha_sel=fecha_sel,
        metodo_sel=metodo_sel, 
        active_page='pagos'
    )

@proceso_pago.route('/cobrar/<int:id_cita>')
@login_required
def pantalla_cobro(id_cita):
    query_detalle = text("""
        SELECT 
            c.id_cita,
            CONCAT(per.nombre_persona, ' ', per.apellidos) AS cliente,
            s.nombre_servicio AS servicio,
            s.precio AS precio_unitario,
            dc.subtotal AS subtotal_original,
            pr.id_promocion,
            pr.nombre AS nombre_promo,
            pr.valor_descuento AS valor_promo
        FROM cita c
        INNER JOIN cliente cl ON c.id_cliente = cl.id_cliente
        INNER JOIN persona per ON cl.id_persona = per.id_persona
        INNER JOIN detalle_cita dc ON c.id_cita = dc.id_cita
        INNER JOIN servicio s ON dc.id_servicio = s.id_servicio
        LEFT JOIN promocion pr ON s.nombre_servicio = pr.tipo_promocion 
        WHERE c.id_cita = :id AND c.estatus = 'FINALIZADA'
    """)
    
    detalle = db.session.execute(query_detalle, {'id': id_cita}).fetchone()
    
    if not detalle:
        flash("Cita no encontrada o no está finalizada", "warning")
        return redirect(url_for('proceso_pago.index'))

    precio_base = float(detalle.subtotal_original or 0)
    monto_descuento = 0.0

    if detalle.valor_promo:
        valor_promo = float(detalle.valor_promo)
        monto_descuento = precio_base * (valor_promo / 100)

    try:
        db.session.execute(
            text("UPDATE detalle_cita SET descuento = :desc WHERE id_cita = :id"),
            {'desc': monto_descuento, 'id': id_cita}
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    subtotal_final = precio_base - monto_descuento
    impuesto_f = subtotal_final * 0.16
    total_f = subtotal_final + impuesto_f

    metodos = db.session.execute(text("SELECT id_metodo_pago, nombre_metodo FROM metodo_pago")).fetchall()
    
    return render_template(
        'pagos/confirmar_pago.html', 
        d=detalle, 
        metodos=metodos, 
        precio_original=precio_base,
        descuento=monto_descuento,
        subtotal=subtotal_final,
        impuesto=impuesto_f,
        total_final=total_f,
        active_page='pagos'
    )

@proceso_pago.route('/registrar-pago', methods=['POST'])
@login_required
def registrar_pago():
    id_cita = request.form.get('id_cita')
    id_metodo = request.form.get('id_metodo_pago')
    total = request.form.get('total')
    
    if not id_metodo:
        flash("Selecciona un método de pago", "warning")
        return redirect(url_for('proceso_pago.index'))

    try:
        total_f = float(total)
        subtotal_pago = total_f / 1.16
        iva_pago = total_f - subtotal_pago

        sql = text("""
            INSERT INTO pago (fecha_pago, subtotal, impuesto, total, id_cita, id_metodo_pago)
            VALUES (NOW(), :sub, :imp, :tot, :cita, :metodo)
        """)
        
        db.session.execute(sql, {
            'sub': subtotal_pago, 'imp': iva_pago, 'tot': total_f,
            'cita': id_cita, 'metodo': id_metodo
        })
        db.session.commit()
        
        id_pago = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        flash("Pago registrado", "success")
        return redirect(url_for('proceso_pago.ver_ticket', id_pago=id_pago))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('proceso_pago.index'))

@proceso_pago.route('/ticket/<int:id_pago>')
@login_required
def ver_ticket(id_pago):
    query_ticket = text("""
        SELECT 
            p.id_pago AS folio, 
            p.fecha_pago,
            CONCAT(per.nombre_persona, ' ', per.apellidos) AS cliente,
            s.nombre_servicio AS servicio,
            dc.subtotal AS precio_original,
            dc.descuento AS monto_descuento,
            p.subtotal AS subtotal_neto,
            p.impuesto,
            p.total,
            mp.nombre_metodo AS metodo
        FROM pago p
        INNER JOIN cita c ON p.id_cita = c.id_cita
        INNER JOIN cliente cl ON c.id_cliente = cl.id_cliente
        INNER JOIN persona per ON cl.id_persona = per.id_persona
        INNER JOIN detalle_cita dc ON c.id_cita = dc.id_cita
        INNER JOIN servicio s ON dc.id_servicio = s.id_servicio
        INNER JOIN metodo_pago mp ON p.id_metodo_pago = mp.id_metodo_pago
        WHERE p.id_pago = :id 
        LIMIT 1
    """)
    ticket = db.session.execute(query_ticket, {'id': id_pago}).fetchone()
    
    if not ticket:
        #flash("Ticket no encontrado", "danger")
        return redirect(url_for('proceso_pago.index'))
        
    return render_template('pagos/ticket.html', t=ticket, active_page='pagos')