from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from . import unidades_bp
import forms
from models import db
from models import UnidadMedida, registrar_log


@unidades_bp.route('/unidades-medida', methods=['GET', 'POST'])
@login_required
def listado_unidades():
    unidades = UnidadMedida.query.order_by(UnidadMedida.nombre_unidad.asc()).all()
    return render_template(
        'unidades/listado_unidades.html',
        unidades=unidades,
        active_page='inventario'
    )


@unidades_bp.route('/unidades-medida/nueva', methods=['GET', 'POST'])
@login_required
def nueva_unidad():
    form = forms.UnidadMedidaForm()

    if form.validate_on_submit():
        existe = db.session.query(UnidadMedida).filter(
            UnidadMedida.nombre_unidad == form.nombre_unidad.data
        ).first()

        if existe:
            flash('Esa unidad ya existe', 'danger')
            return render_template(
                'unidades/unidad_form.html',
                form=form,
                unidad=None,
                active_page='inventario'
            )

        nueva = UnidadMedida(
            nombre_unidad=form.nombre_unidad.data
        )

        try:
            db.session.add(nueva)
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_UNIDAD_MEDIDA",
                tabla="unidad_medida",
                registro_id=nueva.id_unidad_medida,
                descripcion=f"Se registró la unidad de medida {nueva.nombre_unidad}"
            )

            flash('Unidad registrada correctamente', 'success')
            return redirect(url_for('unidades_bp.listado_unidades'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar unidad: {str(e)}', 'danger')

    return render_template(
        'unidades/unidad_form.html',
        form=form,
        unidad=None,
        active_page='inventario'
    )


@unidades_bp.route('/unidades-medida/editar', methods=['GET', 'POST'])
@login_required
def editar_unidad():
    form = forms.UnidadMedidaForm()

    if request.method == 'GET':
        id_unidad = request.args.get('id')
        unidad = db.session.query(UnidadMedida).filter(
            UnidadMedida.id_unidad_medida == id_unidad
        ).first()

        if not unidad:
            flash('Unidad no encontrada', 'danger')
            return redirect(url_for('unidades_bp.listado_unidades'))

        form.id.data = unidad.id_unidad_medida
        form.nombre_unidad.data = unidad.nombre_unidad

        return render_template(
            'unidades/unidad_form.html',
            form=form,
            unidad=unidad,
            active_page='inventario'
        )

    if form.validate_on_submit():
        unidad = db.session.query(UnidadMedida).filter(
            UnidadMedida.id_unidad_medida == form.id.data
        ).first()

        if not unidad:
            flash('Unidad no encontrada', 'danger')
            return redirect(url_for('unidades_bp.listado_unidades'))

        try:
            unidad.nombre_unidad = form.nombre_unidad.data
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_UNIDAD_MEDIDA",
                tabla="unidad_medida",
                registro_id=unidad.id_unidad_medida,
                descripcion=f"Se modificó la unidad de medida {unidad.nombre_unidad}"
            )

            flash('Unidad actualizada correctamente', 'success')
            return redirect(url_for('unidades_bp.listado_unidades'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar unidad: {str(e)}', 'danger')

    return redirect(url_for('unidades_bp.listado_unidades'))


@unidades_bp.route('/unidades-medida/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_unidad():
    form = forms.UnidadMedidaForm()
    unidad = None

    if request.method == 'GET':
        id_unidad = request.args.get('id')
        unidad = db.session.query(UnidadMedida).filter(
            UnidadMedida.id_unidad_medida == id_unidad
        ).first()

        if not unidad:
            flash('Unidad no encontrada', 'danger')
            return redirect(url_for('unidades_bp.listado_unidades'))

        form.id.data = unidad.id_unidad_medida
        form.nombre_unidad.data = unidad.nombre_unidad

    if request.method == 'POST':
        unidad = db.session.query(UnidadMedida).filter(
            UnidadMedida.id_unidad_medida == form.id.data
        ).first()

        if unidad:
            try:
                nombre_unidad = unidad.nombre_unidad
                id_registro = unidad.id_unidad_medida

                db.session.delete(unidad)
                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "BAJA_UNIDAD_MEDIDA",
                    tabla="unidad_medida",
                    registro_id=id_registro,
                    descripcion=f"Se eliminó la unidad de medida {nombre_unidad}"
                )

                flash('Unidad eliminada correctamente', 'warning')

            except Exception as e:
                db.session.rollback()
                flash(f'Error al eliminar unidad: {str(e)}', 'danger')

        return redirect(url_for('unidades_bp.listado_unidades'))

    return render_template(
        'unidades/eliminar_unidad.html',
        form=form,
        unidad=unidad,
        active_page='inventario'
    )