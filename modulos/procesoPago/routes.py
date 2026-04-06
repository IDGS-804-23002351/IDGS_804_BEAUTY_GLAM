from flask import render_template, request
from . import proceso_pago
from models import db
from sqlalchemy import text
from flask_login import login_required

@proceso_pago.route('/pagos', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('search', '')
    metodo_sel = request.args.get('metodo', '')
    fecha_sel = request.args.get('fecha', '')

    query_text = """
        SELECT 
            CONCAT('BG-', p.id_pago) AS folio,
            CONCAT(per.nombre_persona, ' ', per.apellidos) AS cliente,
            s.nombre_servicio AS servicio,
            p.total AS total,
            mp.nombre_metodo AS metodo,
            DATE(p.fecha_pago) AS fecha
        FROM pago p
        INNER JOIN cita c ON p.id_cita = c.id_cita
        INNER JOIN cliente cl ON c.id_cliente = cl.id_cliente
        INNER JOIN persona per ON cl.id_persona = per.id_persona
        INNER JOIN detalle_cita dc ON c.id_cita = dc.id_cita
        INNER JOIN servicio s ON dc.id_servicio = s.id_servicio
        INNER JOIN metodo_pago mp ON p.id_metodo_pago = mp.id_metodo_pago
        WHERE 1=1
    """
    
    params = {}

    if search_query:
        query_text += " AND (per.nombre_persona LIKE :search OR p.id_pago LIKE :search)"
        params['search'] = f"%{search_query}%"
    
    if metodo_sel:
        query_text += " AND mp.nombre_metodo = :metodo"
        params['metodo'] = metodo_sel

    if fecha_sel:
        query_text += " AND DATE(p.fecha_pago) = :fecha"
        params['fecha'] = fecha_sel

    query_text += " ORDER BY p.fecha_pago DESC"

    pagos = db.session.execute(text(query_text), params).fetchall()

    metodos = db.session.execute(text("SELECT nombre_metodo FROM metodo_pago")).fetchall()

    return render_template(
        'pagos/pagos.html', 
        pagos=pagos, 
        metodos=metodos,
        busqueda=search_query,
        fecha_sel=fecha_sel,
        metodo_sel=metodo_sel
    )

@proceso_pago.route('/ticket/<int:id_pago>')
@login_required
def ver_ticket(id_pago):
    query_ticket = text("""
        SELECT 
            p.id_pago AS folio,
            p.fecha_pago,
            CONCAT(per.nombre_persona, ' ', per.apellidos) AS cliente,
            s.nombre_servicio AS servicio,
            s.precio AS precio_unitario,
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
    """)
    
    ticket = db.session.execute(query_ticket, {'id': id_pago}).fetchone()
    
    if not ticket:
        return "Ticket no encontrado", 404

    return render_template('pagos/ticket.html', t=ticket)