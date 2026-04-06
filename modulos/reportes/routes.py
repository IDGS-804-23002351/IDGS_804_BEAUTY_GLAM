from flask import render_template, request
from . import reporte
from models import db
from sqlalchemy import text
from flask_login import login_required
from datetime import datetime

@reporte.route('/reporte', methods=['GET'])
@login_required
def index():
    fecha_sel = request.args.get('fecha')
    mes_sel = request.args.get('mes')
    anio_sel = request.args.get('anio', datetime.now().year)

    if fecha_sel:
        condicion_pago = text("DATE(p.fecha_pago) = :f")
        params = {'f': fecha_sel}
    elif mes_sel:
        condicion_pago = text("MONTH(p.fecha_pago) = :m AND YEAR(p.fecha_pago) = :a")
        params = {'m': mes_sel, 'a': anio_sel}
    else:
        fecha_sel = datetime.now().strftime('%Y-%m-%d')
        condicion_pago = text("DATE(p.fecha_pago) = :f")
        params = {'f': fecha_sel}

    query_ingresos = text(f"""
        SELECT 
            DATE(p.fecha_pago) AS fecha, 
            SUM(p.total) AS total_ingreso,
            COUNT(p.id_pago) AS total_ventas
        FROM pago p
        WHERE {condicion_pago}
        GROUP BY DATE(p.fecha_pago)
        ORDER BY fecha DESC
    """)
    ingresos_diarios = db.session.execute(query_ingresos, params).fetchall()

    query_frecuencia = text(f"""
        SELECT 
            s.nombre_servicio, 
            COUNT(dc.id_detalle_cita) AS veces_realizado,
            SUM(dc.subtotal) AS monto_generado
        FROM detalle_cita dc
        JOIN servicio s ON dc.id_servicio = s.id_servicio
        JOIN cita c ON dc.id_cita = c.id_cita
        JOIN pago p ON c.id_cita = p.id_cita
        WHERE {condicion_pago}
        GROUP BY s.id_servicio, s.nombre_servicio
        ORDER BY veces_realizado DESC
    """)
    frecuencia_servicios = db.session.execute(query_frecuencia, params).fetchall()

    query_materiales = text(f"""
        SELECT 
            prod.nombre AS producto,
            SUM(ins.cantidad_utilizada) AS cantidad_total,
            um.nombre_unidad
        FROM detalle_cita dc
        JOIN insumo_servicio ins ON dc.id_servicio = ins.id_servicio
        JOIN producto prod ON ins.codigo_producto = prod.codigo_producto
        JOIN unidad_medida um ON prod.id_unidad_medida = um.id_unidad_medida
        JOIN cita c ON dc.id_cita = c.id_cita
        JOIN pago p ON c.id_cita = p.id_cita
        WHERE {condicion_pago}
        GROUP BY prod.codigo_producto, prod.nombre, um.nombre_unidad
    """)
    uso_materiales = db.session.execute(query_materiales, params).fetchall()

    return render_template(
        'reportes/reporte.html', 
        ingresos=ingresos_diarios,
        frecuencia=frecuencia_servicios,
        materiales=uso_materiales,
        fecha_sel=fecha_sel,
        mes_sel=mes_sel,
        anio_sel=anio_sel
    )