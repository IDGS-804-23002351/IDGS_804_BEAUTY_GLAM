import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, current_app, session

from . import servicios_bp
import forms
from models import db
from models import Servicio, Categoria, Producto, InsumoServicio, registrar_log
from flask_login import login_required


def guardar_imagen_servicio(archivo):
    if not archivo or archivo.filename == '':
        return None

    nombre_seguro = secure_filename(archivo.filename)
    extension = os.path.splitext(nombre_seguro)[1]
    nuevo_nombre = f"{uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, 'uploads', 'servicios')
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_completa = os.path.join(carpeta_destino, nuevo_nombre)
    archivo.save(ruta_completa)

    return f"uploads/servicios/{nuevo_nombre}"


@servicios_bp.route('/servicios', methods=['GET', 'POST'])
@login_required
def listado_servicios():
    filtro_form = forms.FiltroServicioForm()

    categorias = Categoria.query.all()
    filtro_form.id_categoria.choices = [(0, 'Todas')] + [
        (c.id_categoria, c.nombre_categoria) for c in categorias
    ]

    query = db.session.query(Servicio)

    estatus = request.args.get('estatus', '')
    id_categoria = request.args.get('id_categoria', '0')
    buscar = request.args.get('buscar', '').strip()

    if estatus:
        query = query.filter(Servicio.estatus == estatus)

    if id_categoria and id_categoria != '0':
        query = query.filter(Servicio.id_categoria == int(id_categoria))

    if buscar:
        query = query.filter(Servicio.nombre_servicio.ilike(f'%{buscar}%'))

    servicios = query.order_by(Servicio.id_servicio.desc()).all()

    return render_template(
        'servicios/listado_servicios.html',
        form=filtro_form,
        servicios=servicios,
        active_page='servicios'
    )


@servicios_bp.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    servicio_form = forms.ServicioForm()

    categorias = Categoria.query.all()
    servicio_form.id_categoria.choices = [
        (c.id_categoria, c.nombre_categoria) for c in categorias
    ]

    if servicio_form.validate_on_submit():
        ruta_foto = None

        if servicio_form.foto.data:
            ruta_foto = guardar_imagen_servicio(servicio_form.foto.data)

        nuevo_servicio = Servicio(
            nombre_servicio=servicio_form.nombre_servicio.data,
            precio=servicio_form.precio.data,
            duracion_minutos=servicio_form.duracion_minutos.data,
            foto=ruta_foto,
            estatus=servicio_form.estatus.data,
            id_categoria=servicio_form.id_categoria.data
        )

        try:
            db.session.add(nuevo_servicio)
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_SERVICIO",
                tabla="servicio",
                registro_id=nuevo_servicio.id_servicio,
                descripcion=f"Se registró el servicio {nuevo_servicio.nombre_servicio}"
            )

            flash('Servicio registrado correctamente. Ahora agrega los insumos de la receta.', 'success')
            return redirect(url_for('servicios_bp.editar_servicio', id=nuevo_servicio.id_servicio))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar servicio: {str(e)}', 'danger')

    return render_template(
        'servicios/servicio_form.html',
        form=servicio_form,
        receta_form=None,
        insumos=[],
        servicio=None,
        active_page='servicios'
    )


@servicios_bp.route('/servicios/detalle', methods=['GET'])
@login_required
def detalle_servicio():
    id_servicio = request.args.get('id')
    servicio = db.session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

    if not servicio:
        flash('Servicio no encontrado', 'danger')
        return redirect(url_for('servicios_bp.listado_servicios'))

    insumos = db.session.query(InsumoServicio).filter(
        InsumoServicio.id_servicio == servicio.id_servicio
    ).all()

    return render_template(
        'servicios/detalle_servicio.html',
        servicio=servicio,
        insumos=insumos,
        active_page='servicios'
    )


@servicios_bp.route('/servicios/editar', methods=['GET', 'POST'])
@login_required
def editar_servicio():
    servicio_form = forms.ServicioForm()
    receta_form = forms.RecetaInsumoForm()

    categorias = Categoria.query.all()
    productos = Producto.query.filter(Producto.estatus == 'ACTIVO').all()

    servicio_form.id_categoria.choices = [
        (c.id_categoria, c.nombre_categoria) for c in categorias
    ]

    receta_form.codigo_producto.choices = [
        (
            p.codigo_producto,
            f"{p.nombre} | Stock: {p.stock_actual} | Unidad: {p.unidad_medida.nombre_unidad if p.unidad_medida else 'N/A'}"
        )
        for p in productos
    ]

    if request.method == 'GET':
        id_servicio = request.args.get('id')
    elif 'guardar_servicio' in request.form:
        id_servicio = servicio_form.id.data
    elif 'agregar_insumo' in request.form:
        id_servicio = receta_form.id_servicio.data
    else:
        id_servicio = None

    servicio = db.session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

    if not servicio:
        flash('Servicio no encontrado', 'danger')
        return redirect(url_for('servicios_bp.listado_servicios'))

    if request.method == 'GET':
        servicio_form.id.data = servicio.id_servicio
        servicio_form.nombre_servicio.data = servicio.nombre_servicio
        servicio_form.precio.data = servicio.precio
        servicio_form.duracion_minutos.data = servicio.duracion_minutos
        servicio_form.id_categoria.data = servicio.id_categoria
        servicio_form.estatus.data = servicio.estatus

    if request.method == 'POST' and 'guardar_servicio' in request.form:
        if servicio_form.validate():
            try:
                servicio.nombre_servicio = servicio_form.nombre_servicio.data
                servicio.precio = servicio_form.precio.data
                servicio.duracion_minutos = servicio_form.duracion_minutos.data
                servicio.id_categoria = servicio_form.id_categoria.data
                servicio.estatus = servicio_form.estatus.data

                if servicio_form.foto.data:
                    ruta_foto = guardar_imagen_servicio(servicio_form.foto.data)
                    if ruta_foto:
                        servicio.foto = ruta_foto

                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "EDICION_SERVICIO",
                    tabla="servicio",
                    registro_id=servicio.id_servicio,
                    descripcion=f"Se modificó el servicio {servicio.nombre_servicio}"
                )

                flash('Servicio actualizado correctamente', 'success')
                return redirect(url_for('servicios_bp.editar_servicio', id=servicio.id_servicio))

            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar servicio: {str(e)}', 'danger')
        else:
            flash('Revisa los datos del servicio', 'danger')

    receta_form.id_servicio.data = str(servicio.id_servicio)

    if request.method == 'POST' and 'agregar_insumo' in request.form:
        if receta_form.validate():
            existe = db.session.query(InsumoServicio).filter(
                InsumoServicio.id_servicio == int(receta_form.id_servicio.data),
                InsumoServicio.codigo_producto == receta_form.codigo_producto.data
            ).first()

            if existe:
                flash('Ese insumo ya está agregado a la receta', 'warning')
            else:
                nuevo_insumo = InsumoServicio(
                    id_servicio=int(receta_form.id_servicio.data),
                    codigo_producto=receta_form.codigo_producto.data,
                    cantidad_utilizada=receta_form.cantidad_utilizada.data
                )

                try:
                    db.session.add(nuevo_insumo)
                    db.session.commit()

                    registrar_log(
                        session.get('user_id', 0),
                        "ALTA_INSUMO_SERVICIO",
                        tabla="insumo_servicio",
                        registro_id=nuevo_insumo.id_insumo_servicio,
                        descripcion=(
                            f"Se agregó el insumo {nuevo_insumo.codigo_producto} "
                            f"al servicio ID {nuevo_insumo.id_servicio} "
                            f"con cantidad {nuevo_insumo.cantidad_utilizada}"
                        )
                    )

                    flash('Insumo agregado correctamente', 'success')

                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al agregar insumo: {str(e)}', 'danger')

            return redirect(url_for('servicios_bp.editar_servicio', id=servicio.id_servicio))
        else:
            flash('Revisa los datos del insumo', 'danger')

    insumos = db.session.query(InsumoServicio).filter(
        InsumoServicio.id_servicio == servicio.id_servicio
    ).all()

    return render_template(
        'servicios/servicio_form.html',
        form=servicio_form,
        receta_form=receta_form,
        insumos=insumos,
        servicio=servicio,
        active_page='servicios'
    )


@servicios_bp.route('/servicios/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_servicio():
    servicio_form = forms.ServicioForm()

    categorias = Categoria.query.all()
    servicio_form.id_categoria.choices = [
        (c.id_categoria, c.nombre_categoria) for c in categorias
    ]

    servicio = None

    if request.method == 'GET':
        id_servicio = request.args.get('id')
        servicio = db.session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

        if not servicio:
            flash('Servicio no encontrado', 'danger')
            return redirect(url_for('servicios_bp.listado_servicios'))

        servicio_form.id.data = servicio.id_servicio
        servicio_form.nombre_servicio.data = servicio.nombre_servicio
        servicio_form.precio.data = servicio.precio
        servicio_form.duracion_minutos.data = servicio.duracion_minutos
        servicio_form.id_categoria.data = servicio.id_categoria
        servicio_form.estatus.data = servicio.estatus

    if request.method == 'POST':
        servicio = db.session.query(Servicio).filter(Servicio.id_servicio == servicio_form.id.data).first()

        if servicio:
            try:
                servicio.estatus = 'INACTIVO'
                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "BAJA_SERVICIO",
                    tabla="servicio",
                    registro_id=servicio.id_servicio,
                    descripcion=f"Se cambió a INACTIVO el servicio {servicio.nombre_servicio}"
                )

                flash('Servicio desactivado correctamente', 'warning')

            except Exception as e:
                db.session.rollback()
                flash(f'Error al desactivar servicio: {str(e)}', 'danger')

        return redirect(url_for('servicios_bp.listado_servicios'))

    return render_template(
        'servicios/eliminar_servicio.html',
        form=servicio_form,
        servicio=servicio,
        active_page='servicios'
    )


@servicios_bp.route('/servicios/insumo/editar', methods=['GET', 'POST'])
@login_required
def editar_insumo_servicio():
    receta_form = forms.RecetaInsumoForm()

    productos = Producto.query.filter(Producto.estatus == 'ACTIVO').all()
    receta_form.codigo_producto.choices = [
        (
            p.codigo_producto,
            f"{p.nombre} | Stock: {p.stock_actual} | Unidad: {p.unidad_medida.nombre_unidad if p.unidad_medida else 'N/A'}"
        )
        for p in productos
    ]

    if request.method == 'GET':
        id_insumo = request.args.get('id')
        insumo = db.session.query(InsumoServicio).filter(InsumoServicio.id_insumo_servicio == id_insumo).first()

        if not insumo:
            flash('Insumo no encontrado', 'danger')
            return redirect(url_for('servicios_bp.listado_servicios'))

        receta_form.id.data = insumo.id_insumo_servicio
        receta_form.id_servicio.data = str(insumo.id_servicio)
        receta_form.codigo_producto.data = insumo.codigo_producto
        receta_form.cantidad_utilizada.data = insumo.cantidad_utilizada

    if request.method == 'POST':
        insumo = db.session.query(InsumoServicio).filter(
            InsumoServicio.id_insumo_servicio == receta_form.id.data
        ).first()

        if insumo and receta_form.validate():
            try:
                insumo.codigo_producto = receta_form.codigo_producto.data
                insumo.cantidad_utilizada = receta_form.cantidad_utilizada.data
                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "EDICION_INSUMO_SERVICIO",
                    tabla="insumo_servicio",
                    registro_id=insumo.id_insumo_servicio,
                    descripcion=(
                        f"Se modificó el insumo {insumo.codigo_producto} "
                        f"del servicio ID {insumo.id_servicio} "
                        f"con cantidad {insumo.cantidad_utilizada}"
                    )
                )

                flash('Insumo actualizado correctamente', 'success')
                return redirect(url_for('servicios_bp.editar_servicio', id=insumo.id_servicio))

            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar insumo: {str(e)}', 'danger')

    flash('No se pudo editar el insumo', 'danger')
    return redirect(url_for('servicios_bp.listado_servicios'))


@servicios_bp.route('/servicios/insumo/eliminar', methods=['GET'])
@login_required
def eliminar_insumo_servicio():
    id_insumo = request.args.get('id')
    insumo = db.session.query(InsumoServicio).filter(
        InsumoServicio.id_insumo_servicio == id_insumo
    ).first()

    if not insumo:
        flash('Insumo no encontrado', 'danger')
        return redirect(url_for('servicios_bp.listado_servicios'))

    id_servicio = insumo.id_servicio

    try:
        db.session.delete(insumo)
        db.session.commit()

        registrar_log(
            session.get('user_id', 0),
            "BAJA_INSUMO_SERVICIO",
            tabla="insumo_servicio",
            registro_id=insumo.id_insumo_servicio,
            descripcion=f"Se eliminó el insumo del servicio ID {id_servicio}"
        )

        flash('Insumo eliminado correctamente', 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar insumo: {str(e)}', 'danger')

    return redirect(url_for('servicios_bp.editar_servicio', id=id_servicio))