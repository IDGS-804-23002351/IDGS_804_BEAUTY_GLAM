from flask import render_template
from models import db, Servicio, Promocion, Categoria
from . import inicio_bp

@inicio_bp.route('/bienvenida')
def inicio_publico():
    promociones_activas = Promocion.query.filter_by(estatus='ACTIVO').all()
    servicios_destacados = Servicio.query.filter_by(estatus='ACTIVO').order_by(Servicio.id_servicio.desc()).limit(6).all()

    categorias = Categoria.query.all()

    return render_template(
        'inicio.html', 
        promociones=promociones_activas, 
        servicios=servicios_destacados,
        categorias=categorias
    )