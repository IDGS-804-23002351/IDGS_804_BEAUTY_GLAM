from flask import Blueprint, render_template, redirect, url_for, flash
from config import bitacora_mongo
from bson.objectid import ObjectId
from . import bitacora_bp
from flask_login import login_required, current_user # Importante para la seguridad
from datetime import datetime
import pytz
from bson import ObjectId

@bitacora_bp.route('/bitacora')
@login_required
def listado_bitacora():
    if current_user.id_rol != 1:
        flash("Acceso denegado: Solo el administrador puede ver la bitácora.", "danger")
        return redirect(url_for('acceso.dashboard'))
        
    registros = list(bitacora_mongo.find().sort('fecha_hora', -1).limit(100)) 

    mx_tz = pytz.timezone('America/Mexico_City')
    
    for reg in registros:
        fecha = reg.get('fecha_hora')
        if fecha and isinstance(fecha, datetime):
            if fecha.tzinfo is None:
                fecha = pytz.utc.localize(fecha)
            
            reg['fecha_hora'] = fecha.astimezone(mx_tz)
        else:
            reg['fecha_hora'] = None
    
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
            
    except Exception as e:
        print(f"Error al buscar en Mongo: {e}")
        flash("ID de bitácora no válido.", "danger")
        return redirect(url_for('bitacora.listado_bitacora'))

    return render_template('bitacora/detalleBitacora.html', evento=evento)