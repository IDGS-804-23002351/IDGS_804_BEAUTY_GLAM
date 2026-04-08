import os
from flask import render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from forms import PromocionForm
from . import promociones
from flask_login import login_required
from models import db, Servicio, Promocion,  registrar_log

@promociones.route("/promociones", methods=['GET'])
@login_required
def index():
    lista_promociones = Promocion.query.filter(Promocion.estatus.in_(['ACTIVO', 'INACTIVO'])).all()
    return render_template("promos/promociones.html", promociones=lista_promociones, active_page='promos')

@promociones.route("/agregar", methods=['GET', 'POST'])
@login_required
def agregar():
    form = PromocionForm()
    lista_servicios = Servicio.query.all()
    
    if form.validate_on_submit():
        try:
            tipo_nuevo = form.tipo_promocion.data
            existe_activa = Promocion.query.filter_by(tipo_promocion=tipo_nuevo, estatus='ACTIVO').first()
            
            if existe_activa:
                flash(f"Ya existe una promoción de tipo '{tipo_nuevo}'.", "warning")
                return render_template("promos/agregar.html", form=form, servicios=lista_servicios, active_page='promos')

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

            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="CREACION_PROMOCION",
                modulo="Promos",
                detalle=f"Se creó la promoción '{form.nombre.data}' con valor de {form.valor_descuento.data}%"
            )

            flash("Promoción agregada exitosamente", "success")
            return redirect(url_for('.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar: {str(e)}", "danger")
    
    return render_template("promos/agregar.html", form=form, servicios=lista_servicios, active_page='promos')

@promociones.route("/actualizar/<int:id>", methods=['GET', 'POST'])
@login_required
def actualizar(id):
    promo = Promocion.query.get_or_404(id)
    form = PromocionForm(obj=promo)
    lista_servicios = Servicio.query.all()
    
    if form.validate_on_submit():
        try:
            tipo_editado = form.tipo_promocion.data
            existe_activa = Promocion.query.filter(
                Promocion.tipo_promocion == tipo_editado,
                Promocion.estatus == 'ACTIVO',
                Promocion.id_promocion != id 
            ).first()

            if existe_activa:
                flash(f"No se puede actualizar: ya hay otra promoción de tipo '{tipo_editado}'.", "warning")
                return render_template("promos/actualizar.html", form=form, promo=promo, servicios=lista_servicios, active_page='promos')

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

            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="EDICION_PROMOCION",
                modulo="Promos",
                detalle=f"Se actualizó la información de la promoción: {promo.nombre}"
            )

            flash("Promoción actualizada con éxito", "success")
            return redirect(url_for('.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "danger")
            
    return render_template("promos/actualizar.html", form=form, promo=promo, servicios=lista_servicios, active_page='promos')

@promociones.route("/eliminar/<int:id>", methods=['GET', 'POST'])
@login_required
def eliminar(id):
    promo = Promocion.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            sql = "CALL eliminar_promocion(:id)"
            db.session.execute(db.text(sql), {'id': id})
            db.session.commit()

            registrar_log(
                usuario_id=session.get('user_id', 0),
                accion="BAJA_PROMOCION",
                modulo="Promos",
                detalle=f"Se cambió el estatus a INACTIVO de la promoción: {promo.nombre}"
            )

            flash(f"La promoción {promo.nombre} ha sido desactivada.", "warning")
            return redirect(url_for('.index')) 
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al desactivar: {str(e)}", "danger")
            return redirect(url_for('.index'))

    form = PromocionForm(obj=promo)
    return render_template("promos/eliminar.html", promo=promo, form=form, active_page='promos')

@promociones.route("/catalogo", methods=['GET'])
def catalogo_clientes():
    lista_promociones = Promocion.query.filter_by(estatus='ACTIVO').all()
    return render_template("vistaClientes/promos/promos.html", promociones=lista_promociones, active_page='promos')