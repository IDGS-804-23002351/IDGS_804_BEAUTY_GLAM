from flask import render_template
from models import db, Servicio, Promocion, Categoria
from . import inicio_bp

@inicio_bp.route('/bienvenida')
def inicio_publico():
    promociones_activas = Promocion.query.filter_by(estatus='ACTIVO').all()
    
    # Obtener todas las categorías
    categorias = Categoria.query.all()
    
    # Agrupar servicios por categoría
    servicios_por_categoria = {}
    total_servicios = 0
    
    for categoria in categorias:
        servicios_cat = Servicio.query.filter_by(
            estatus='ACTIVO',
            id_categoria=categoria.id_categoria
        ).order_by(Servicio.nombre_servicio.asc()).all()
        
        if servicios_cat:
            servicios_por_categoria[categoria.nombre_categoria] = servicios_cat
            total_servicios += len(servicios_cat)
    
    # Servicios sin categoría
    servicios_sin_categoria = Servicio.query.filter_by(
        estatus='ACTIVO'
    ).filter(Servicio.id_categoria == None).order_by(Servicio.nombre_servicio.asc()).all()
    
    if servicios_sin_categoria:
        servicios_por_categoria['Otros Servicios'] = servicios_sin_categoria
        total_servicios += len(servicios_sin_categoria)

    return render_template(
        'inicio.html',
        promociones=promociones_activas,
        servicios_por_categoria=servicios_por_categoria,
        categorias=categorias,
        total_servicios=total_servicios  # ← Pasamos el total calculado
    )