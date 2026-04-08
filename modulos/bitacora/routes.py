from flask import Blueprint, render_template, redirect, url_for, flash
from config import bitacora_mongo
from bson.objectid import ObjectId
from . import bitacora_bp
from flask_login import login_required, current_user 
from datetime import datetime
from flask import request 
from models import Usuario
import pytz
from bson import ObjectId

@bitacora_bp.route('/bitacora')
@login_required
def listado_bitacora():
    if current_user.id_rol != 1:
        flash("Acceso denegado: Solo el administrador puede ver la bitácora.", "danger")
        return redirect(url_for('acceso.dashboard'))
    
    f_usuario = request.args.get('usuario', '').strip()
    f_modulo = request.args.get('modulo', '')
    f_fecha = request.args.get('fecha', '')

    query = {}
    
    if f_modulo:
        query['tabla_afectada'] = f_modulo
        
    if f_fecha:
        try:
            fecha_inicio = datetime.strptime(f_fecha, '%Y-%m-%d')
            fecha_fin = fecha_inicio.replace(hour=23, minute=59, second=59)
            
            query['fecha_hora'] = {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        except ValueError:
            pass

    registros = list(bitacora_mongo.find(query).sort('fecha_hora', -1).limit(100)) 

    mx_tz = pytz.timezone('America/Mexico_City')
    
    for reg in registros:
        fecha = reg.get('fecha_hora')
        if fecha and isinstance(fecha, datetime):
            if fecha.tzinfo is None:
                fecha = pytz.utc.localize(fecha)
            reg['fecha_hora'] = fecha.astimezone(mx_tz)
        
        user_id = reg.get('id_usuario')
        user_db = Usuario.query.get(user_id) if user_id else None
        
        reg['nombre_usuario_display'] = user_db.nombre_usuario if user_db else f"ID: {user_id}"

    if f_usuario:
        registros = [r for r in registros if f_usuario.lower() in r['nombre_usuario_display'].lower()]

    return render_template('bitacora/listadoBitacora.html', registros=registros)

@bitacora_bp.route('/bitacora/detalle/<id>')
@login_required
def bitacora_detalle(id):
    if current_user.id_rol != 1:
        flash("No tienes permisos para ver detalles de auditoría.", "danger")
        return redirect(url_for('acceso.dashboard'))
    
    try:
        evento = bitacora_mongo.find_one({"_id": ObjectId(id)})
        
        if not evento:
            flash("El registro de auditoría no existe.", "warning")
            return redirect(url_for('bitacora.listado_bitacora'))

        mx_tz = pytz.timezone('America/Mexico_City')
        fecha = evento.get('fecha_hora')
        
        if fecha and isinstance(fecha, datetime):
            if fecha.tzinfo is None:
                fecha = pytz.utc.localize(fecha)
            evento['fecha_hora'] = fecha.astimezone(mx_tz)
        
        user_id = evento.get('id_usuario')
        user_db = Usuario.query.get(user_id) if user_id else None
        
        evento['nombre_usuario_display'] = user_db.nombre_usuario if user_db else f"ID: {user_id}"
            
    except Exception as e:
        print(f"Error al buscar en Mongo: {e}")
        flash("ID de bitácora no válido o error de conexión.", "danger")
        return redirect(url_for('bitacora.listado_bitacora'))

    return render_template('bitacora/detalleBitacora.html', evento=evento)