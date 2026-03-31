import os
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from forms import PromocionForm
from . import promociones
from models import db, Promocion

@promociones.route("/promociones", methods=['GET'])
def index():
    lista_promociones = Promocion.query.filter_by(estatus='ACTIVO').all()
    return render_template("promos/promociones.html", promociones=lista_promociones)

@promociones.route("/agregar", methods=['GET', 'POST'])
def agregar():
    form = PromocionForm()
    if form.validate_on_submit():
        try:
            nombre_archivo = None
            if form.foto.data:
                f = form.foto.data
                nombre_archivo = secure_filename(f.filename)
                ruta_carpeta = os.path.join(current_app.root_path, 'static', 'img', 'promociones')
                
                if not os.path.exists(ruta_carpeta):
                    os.makedirs(ruta_carpeta)
                
                f.save(os.path.join(ruta_carpeta, nombre_archivo))

            sql = "CALL agregar_promocion(:nombre, :tipo, :desc, :valor, :foto)"
            db.session.execute(db.text(sql), {
                'nombre': form.nombre.data,
                'tipo': form.tipo_promocion.data,
                'desc': form.descripcion.data,
                'valor': form.valor_descuento.data,
                'foto': nombre_archivo
            })
            
            db.session.commit()
            flash("Promoción agregada exitosamente")
            return redirect(url_for('.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar: {str(e)}")
    
    return render_template("promos/agregar.html", form=form)

@promociones.route("/actualizar/<int:id>", methods=['GET', 'POST'])
def actualizar(id):
    promo = Promocion.query.get_or_404(id)
    form = PromocionForm(obj=promo)
    
    if form.validate_on_submit():
        try:
            nombre_archivo_viejo = promo.foto 
            nombre_archivo_nuevo = nombre_archivo_viejo
            
            if form.foto.data and hasattr(form.foto.data, 'filename') and form.foto.data.filename != '':
                f = form.foto.data
                nombre_archivo_nuevo = secure_filename(f.filename)
                ruta_carpeta = os.path.join(current_app.root_path, 'static', 'img', 'promociones')

                if not os.path.exists(ruta_carpeta):
                    os.makedirs(ruta_carpeta)
                
                f.save(os.path.join(ruta_carpeta, nombre_archivo_nuevo))

                if nombre_archivo_viejo and nombre_archivo_viejo != nombre_archivo_nuevo:
                    ruta_vieja = os.path.join(ruta_carpeta, nombre_archivo_viejo)
                    if os.path.exists(ruta_vieja):
                        os.remove(ruta_vieja)

            sql = "CALL actualizar_promocion(:id, :nombre, :tipo, :desc, :valor, :foto)"
            db.session.execute(db.text(sql), {
                'id': id,
                'nombre': form.nombre.data,
                'tipo': form.tipo_promocion.data,
                'desc': form.descripcion.data,
                'valor': form.valor_descuento.data,
                'foto': nombre_archivo_nuevo
            })

            db.session.commit()
            flash("Promoción actualizada con éxito")
            return redirect(url_for('.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}")
            
    return render_template("promos/actualizar.html", form=form, promo=promo)

@promociones.route("/eliminar/<int:id>", methods=['GET', 'POST'])
def eliminar(id):
    promo = Promocion.query.get_or_404(id)
    
    form = PromocionForm(obj=promo)
    
    if request.method == 'POST':
        try:
            sql = "CALL eliminar_promocion(:id)"
            db.session.execute(db.text(sql), {'id': id})
            db.session.commit()
            flash("Promoción desactivada correctamente")
            return redirect(url_for('.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al desactivar: {str(e)}")
            return redirect(url_for('.index'))
    
    return render_template("promos/eliminar.html", promo=promo, form=form)

@promociones.route("/detalles/<int:id>")
def detalles(id):
    promo = Promocion.query.get_or_404(id)
    return render_template("promos/detalles.html", promo=promo)