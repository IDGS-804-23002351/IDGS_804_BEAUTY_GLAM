from flask import render_template, request, redirect, url_for, flash, session

from . import marcas_bp
import forms
from models import db
from models import Marca, Empresa, registrar_log


@marcas_bp.route('/marcas', methods=['GET', 'POST'])
def listado_marcas():
    marcas = Marca.query.order_by(Marca.nombre_marca.asc()).all()
    return render_template(
        'marcas/listado_marcas.html',
        marcas=marcas,
        active_page='inventario'
    )


@marcas_bp.route('/marcas/nueva', methods=['GET', 'POST'])
def nueva_marca():
    form = forms.MarcaForm()

    if form.validate_on_submit():
        empresa = db.session.query(Empresa).filter(Empresa.rfc == form.rfc.data).first()

        if not empresa:
            flash('No existe una empresa con ese RFC', 'danger')
            return render_template(
                'marcas/marca_form.html',
                form=form,
                marca=None,
                active_page='inventario'
            )

        nueva = Marca(
            nombre_marca=form.nombre_marca.data,
            estatus=form.estatus.data,
            rfc=form.rfc.data
        )

        try:
            db.session.add(nueva)
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_MARCA",
                tabla="marca",
                registro_id=nueva.id_marca,
                descripcion=f"Se registró la marca {nueva.nombre_marca}"
            )

            flash('Marca registrada correctamente', 'success')
            return redirect(url_for('marcas_bp.listado_marcas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar marca: {str(e)}', 'danger')

    return render_template(
        'marcas/marca_form.html',
        form=form,
        marca=None,
        active_page='inventario'
    )


@marcas_bp.route('/marcas/editar', methods=['GET', 'POST'])
def editar_marca():
    form = forms.MarcaForm()

    if request.method == 'GET':
        id_marca = request.args.get('id')
        marca = db.session.query(Marca).filter(Marca.id_marca == id_marca).first()

        if not marca:
            flash('Marca no encontrada', 'danger')
            return redirect(url_for('marcas_bp.listado_marcas'))

        form.id.data = marca.id_marca
        form.nombre_marca.data = marca.nombre_marca
        form.rfc.data = marca.rfc
        form.estatus.data = marca.estatus

        return render_template(
            'marcas/marca_form.html',
            form=form,
            marca=marca,
            active_page='inventario'
        )

    if form.validate_on_submit():
        marca = db.session.query(Marca).filter(Marca.id_marca == form.id.data).first()

        if not marca:
            flash('Marca no encontrada', 'danger')
            return redirect(url_for('marcas_bp.listado_marcas'))

        empresa = db.session.query(Empresa).filter(Empresa.rfc == form.rfc.data).first()

        if not empresa:
            flash('No existe una empresa con ese RFC', 'danger')
            return render_template(
                'marcas/marca_form.html',
                form=form,
                marca=marca,
                active_page='inventario'
            )

        try:
            marca.nombre_marca = form.nombre_marca.data
            marca.rfc = form.rfc.data
            marca.estatus = form.estatus.data

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_MARCA",
                tabla="marca",
                registro_id=marca.id_marca,
                descripcion=f"Se modificó la marca {marca.nombre_marca}"
            )

            flash('Marca actualizada correctamente', 'success')
            return redirect(url_for('marcas_bp.listado_marcas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar marca: {str(e)}', 'danger')

    return redirect(url_for('marcas_bp.listado_marcas'))


@marcas_bp.route('/marcas/eliminar', methods=['GET', 'POST'])
def eliminar_marca():
    form = forms.MarcaForm()
    marca = None

    if request.method == 'GET':
        id_marca = request.args.get('id')
        marca = db.session.query(Marca).filter(Marca.id_marca == id_marca).first()

        if not marca:
            flash('Marca no encontrada', 'danger')
            return redirect(url_for('marcas_bp.listado_marcas'))

        form.id.data = marca.id_marca
        form.nombre_marca.data = marca.nombre_marca
        form.rfc.data = marca.rfc
        form.estatus.data = marca.estatus

    if request.method == 'POST':
        marca = db.session.query(Marca).filter(Marca.id_marca == form.id.data).first()

        if marca:
            try:
                marca.estatus = 'INACTIVO'
                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "BAJA_MARCA",
                    tabla="marca",
                    registro_id=marca.id_marca,
                    descripcion=f"Se cambió a INACTIVO la marca {marca.nombre_marca}"
                )

                flash('Marca desactivada correctamente', 'warning')

            except Exception as e:
                db.session.rollback()
                flash(f'Error al desactivar marca: {str(e)}', 'danger')

        return redirect(url_for('marcas_bp.listado_marcas'))

    return render_template(
        'marcas/eliminar_marca.html',
        form=form,
        marca=marca,
        active_page='inventario'
    )