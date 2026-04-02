# modulos/bitacora/routes.py
from flask import Blueprint, render_template, session, redirect, url_for
from config import bitacora_mongo
from bson.objectid import ObjectId
from . import bitacora_bp


@bitacora_bp.route('/bitacora')
def listado_bitacora():
    # Seguridad: Solo admin
    if session.get('user_rol') != 'Administrador':
        return redirect(url_for('acceso.dashboard'))
        
    # Traer todos los logs de Mongo ordenados por fecha
    registros = list(bitacora_mongo.find().sort('fecha', -1)) 
    return render_template('bitacora/listadoBitacora.html', registros=registros)

@bitacora_bp.route('/bitacora/detalle/<id>')
def bitacora_detalle(id):
    if session.get('user_rol') != 'Administrador':
        return redirect(url_for('acceso.dashboard'))
    
    try:
        # Convertimos el string id a un ObjectId de MongoDB
        evento = bitacora_mongo.find_one({"_id": ObjectId(id)})
        
        # Esto te ayudará a ver en la terminal si se encontró algo
        print(f"Buscando ID: {id} -> Resultado: {evento}")
        
    except Exception as e:
        print(f"Error al buscar en Mongo: {e}")
        evento = None

    return render_template('bitacora/detalleBitacora.html', evento=evento)