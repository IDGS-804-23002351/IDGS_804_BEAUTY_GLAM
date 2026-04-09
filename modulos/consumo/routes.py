from flask import render_template, request, redirect, url_for, flash, session
import forms
from . import consumo_bp
from models import db
from models import MovimientoInventario, Producto, registrar_log
from flask_login import login_required


@consumo_bp.route('/consumo', methods=['GET', 'POST'])
@login_required
def listado_consumo():
    filtro_form = forms.FiltroConsumoForm()

    buscar = request.args.get('buscar', '').strip()
    tipo = request.args.get('tipo', '')

    query = db.session.query(MovimientoInventario).filter(
        MovimientoInventario.tipo.in_(['SALIDA', 'AJUSTE'])
    )

    if tipo:
        query = query.filter(MovimientoInventario.tipo == tipo)

    if buscar:
        query = query.join(
            Producto,
            Producto.codigo_producto == MovimientoInventario.codigo_producto
        ).filter(
            db.or_(
                Producto.nombre.ilike(f'%{buscar}%'),
                MovimientoInventario.motivo.ilike(f'%{buscar}%')
            )
        )

    movimientos = query.order_by(MovimientoInventario.fecha.desc()).all()

    return render_template(
        'consumo/listado_consumo.html',
        form=filtro_form,
        movimientos=movimientos,
        active_page='consumo'
    )


@consumo_bp.route('/consumo/detalle', methods=['GET'])
@login_required
def detalle_consumo():
    id_movimiento = request.args.get('id')
    movimiento = db.session.query(MovimientoInventario).filter(
        MovimientoInventario.id_movimiento == id_movimiento
    ).first()

    if not movimiento:
        flash('Movimiento no encontrado', 'danger')
        return redirect(url_for('consumo_bp.listado_consumo'))

    producto = db.session.query(Producto).filter(
        Producto.codigo_producto == movimiento.codigo_producto
    ).first()

    return render_template(
        'consumo/detalle_consumo.html',
        movimiento=movimiento,
        producto=producto,
        active_page='consumo'
    )


@consumo_bp.route('/consumo/ajuste', methods=['GET', 'POST'])
@login_required
def ajuste_manual_consumo():
    form = forms.AjusteConsumoForm()

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == codigo_producto
        ).first()

        if not producto:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('consumo_bp.listado_consumo'))

        form.codigo_producto.data = producto.codigo_producto

        return render_template(
            'consumo/ajuste_consumo.html',
            form=form,
            producto=producto,
            active_page='consumo'
        )

    if form.validate_on_submit():
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == form.codigo_producto.data
        ).first()

        if not producto:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('consumo_bp.listado_consumo'))

        if producto.stock_actual < form.cantidad.data:
            flash('No hay suficiente stock para hacer el ajuste', 'danger')
            return redirect(url_for('consumo_bp.ajuste_manual_consumo', codigo=producto.codigo_producto))

        movimiento = MovimientoInventario(
            codigo_producto=producto.codigo_producto,
            tipo='AJUSTE',
            cantidad=form.cantidad.data,
            motivo=form.motivo.data
        )

        try:
            producto.stock_actual -= form.cantidad.data

            db.session.add(movimiento)
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "AJUSTE_INVENTARIO",
                tabla="movimiento_inventario",
                registro_id=movimiento.id_movimiento,
                descripcion=(
                    f"Se registró un ajuste manual del producto {producto.codigo_producto} "
                    f"por cantidad {movimiento.cantidad}. Motivo: {movimiento.motivo}"
                )
            )

            flash('Ajuste manual registrado correctamente', 'success')
            return redirect(url_for('consumo_bp.detalle_consumo', id=movimiento.id_movimiento))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar ajuste: {str(e)}', 'danger')
            return render_template(
                'consumo/ajuste_consumo.html',
                form=form,
                producto=producto,
                active_page='consumo'
            )

    flash('Revisa los datos del ajuste', 'danger')
    return redirect(url_for('consumo_bp.listado_consumo'))