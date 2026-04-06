from flask import render_template, request, redirect, url_for, flash, session

from . import materias_primas_bp
import forms
from models import db
from models import (
    Producto, Marca, UnidadMedida, InventarioProducto,
    MovimientoInventario, registrar_log
)


@materias_primas_bp.route('/materias-primas', methods=['GET', 'POST'])
def listado_productos():
    filtro_form = forms.FiltroProductoForm()

    marcas = Marca.query.all()
    unidades = UnidadMedida.query.all()

    filtro_form.id_marca.choices = [(0, 'Todas')] + [
        (m.id_marca, m.nombre_marca) for m in marcas
    ]

    filtro_form.id_unidad_medida.choices = [(0, 'Todas')] + [
        (u.id_unidad_medida, u.nombre_unidad) for u in unidades
    ]

    query = db.session.query(Producto)

    estatus = request.args.get('estatus', '')
    id_marca = request.args.get('id_marca', '0')
    id_unidad_medida = request.args.get('id_unidad_medida', '0')
    buscar = request.args.get('buscar', '').strip()

    if estatus:
        query = query.filter(Producto.estatus == estatus)

    if id_marca and id_marca != '0':
        query = query.filter(Producto.id_marca == int(id_marca))

    if id_unidad_medida and id_unidad_medida != '0':
        query = query.filter(Producto.id_unidad_medida == int(id_unidad_medida))

    if buscar:
        query = query.filter(Producto.nombre.ilike(f'%{buscar}%'))

    productos = query.order_by(Producto.nombre.asc()).all()

    return render_template(
        'materias_primas/listado_productos.html',
        form=filtro_form,
        productos=productos,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    producto_form = forms.ProductoForm()

    marcas = Marca.query.filter(Marca.estatus == 'ACTIVO').all()
    unidades = UnidadMedida.query.all()

    producto_form.id_marca.choices = [(m.id_marca, m.nombre_marca) for m in marcas]
    producto_form.id_unidad_medida.choices = [(u.id_unidad_medida, u.nombre_unidad) for u in unidades]

    if producto_form.validate_on_submit():
        existe = db.session.query(Producto).filter(
            Producto.codigo_producto == producto_form.codigo_producto.data
        ).first()

        if existe:
            flash('Ya existe una materia prima con ese código', 'danger')
            return render_template(
                'materias_primas/productos_form.html',
                form=producto_form,
                producto=None,
                active_page='inventario'
            )

        nuevo_producto = Producto(
            codigo_producto=producto_form.codigo_producto.data,
            nombre=producto_form.nombre.data,
            stock_actual=producto_form.stock_actual.data,
            precio_compra=producto_form.precio_compra.data,
            precio_unitario=producto_form.precio_unitario.data,
            estatus=producto_form.estatus.data,
            id_marca=producto_form.id_marca.data,
            id_unidad_medida=producto_form.id_unidad_medida.data
        )

        try:
            db.session.add(nuevo_producto)
            db.session.flush()

            inventario = InventarioProducto(
                codigo_producto=nuevo_producto.codigo_producto,
                stock_minimo=producto_form.stock_minimo.data,
                stock_maximo=producto_form.stock_maximo.data
            )
            db.session.add(inventario)

            movimiento = MovimientoInventario(
                codigo_producto=nuevo_producto.codigo_producto,
                tipo='ENTRADA',
                cantidad=producto_form.stock_actual.data,
                motivo='Registro inicial de materia prima'
            )
            db.session.add(movimiento)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_MATERIA_PRIMA",
                tabla="producto",
                registro_id=0,
                descripcion=f"Se registró la materia prima {nuevo_producto.nombre} con código {nuevo_producto.codigo_producto}"
            )

            registrar_log(
                session.get('user_id', 0),
                "MOVIMIENTO_INVENTARIO",
                tabla="movimiento_inventario",
                registro_id=movimiento.id_movimiento,
                descripcion=f"Entrada inicial de inventario para {nuevo_producto.codigo_producto} por cantidad {movimiento.cantidad}"
            )

            flash('Materia prima registrada correctamente', 'success')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar materia prima: {str(e)}', 'danger')

    return render_template(
        'materias_primas/productos_form.html',
        form=producto_form,
        producto=None,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/detalle', methods=['GET'])
def detalle_producto():
    codigo_producto = request.args.get('codigo')
    producto = db.session.query(Producto).filter(
        Producto.codigo_producto == codigo_producto
    ).first()

    if not producto:
        flash('Materia prima no encontrada', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

    inventario = db.session.query(InventarioProducto).filter(
        InventarioProducto.codigo_producto == producto.codigo_producto
    ).first()

    movimientos = db.session.query(MovimientoInventario).filter(
        MovimientoInventario.codigo_producto == producto.codigo_producto
    ).order_by(MovimientoInventario.fecha.desc()).all()

    return render_template(
        'materias_primas/detalle_producto.html',
        producto=producto,
        inventario=inventario,
        movimientos=movimientos,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/editar', methods=['GET', 'POST'])
def editar_producto():
    producto_form = forms.ProductoForm()

    marcas = Marca.query.filter(Marca.estatus == 'ACTIVO').all()
    unidades = UnidadMedida.query.all()

    producto_form.id_marca.choices = [(m.id_marca, m.nombre_marca) for m in marcas]
    producto_form.id_unidad_medida.choices = [(u.id_unidad_medida, u.nombre_unidad) for u in unidades]

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == codigo_producto
        ).first()

        if not producto:
            flash('Materia prima no encontrada', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        producto_form.codigo_producto.data = producto.codigo_producto
        producto_form.nombre.data = producto.nombre
        producto_form.stock_actual.data = producto.stock_actual
        producto_form.precio_compra.data = producto.precio_compra
        producto_form.precio_unitario.data = producto.precio_unitario
        producto_form.estatus.data = producto.estatus
        producto_form.id_marca.data = producto.id_marca
        producto_form.id_unidad_medida.data = producto.id_unidad_medida
        producto_form.stock_minimo.data = inventario.stock_minimo if inventario else 0
        producto_form.stock_maximo.data = inventario.stock_maximo if inventario else 0

        return render_template(
            'materias_primas/productos_form.html',
            form=producto_form,
            producto=producto,
            active_page='inventario'
        )

    if producto_form.validate_on_submit():
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == producto_form.codigo_producto.data
        ).first()

        if not producto:
            flash('Materia prima no encontrada', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        stock_anterior = producto.stock_actual

        try:
            producto.nombre = producto_form.nombre.data
            producto.stock_actual = producto_form.stock_actual.data
            producto.precio_compra = producto_form.precio_compra.data
            producto.precio_unitario = producto_form.precio_unitario.data
            producto.estatus = producto_form.estatus.data
            producto.id_marca = producto_form.id_marca.data
            producto.id_unidad_medida = producto_form.id_unidad_medida.data

            if inventario:
                inventario.stock_minimo = producto_form.stock_minimo.data
                inventario.stock_maximo = producto_form.stock_maximo.data
            else:
                inventario = InventarioProducto(
                    codigo_producto=producto.codigo_producto,
                    stock_minimo=producto_form.stock_minimo.data,
                    stock_maximo=producto_form.stock_maximo.data
                )
                db.session.add(inventario)

            movimiento = None

            if stock_anterior != producto_form.stock_actual.data:
                diferencia = producto_form.stock_actual.data - stock_anterior

                if diferencia > 0:
                    tipo = 'ENTRADA'
                    cantidad = diferencia
                    motivo = 'Ajuste manual de stock'
                else:
                    tipo = 'SALIDA'
                    cantidad = abs(diferencia)
                    motivo = 'Ajuste manual de stock'

                movimiento = MovimientoInventario(
                    codigo_producto=producto.codigo_producto,
                    tipo=tipo,
                    cantidad=cantidad,
                    motivo=motivo
                )
                db.session.add(movimiento)

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_MATERIA_PRIMA",
                tabla="producto",
                registro_id=0,
                descripcion=f"Se modificó la materia prima {producto.nombre} con código {producto.codigo_producto}"
            )

            if movimiento:
                registrar_log(
                    session.get('user_id', 0),
                    "MOVIMIENTO_INVENTARIO",
                    tabla="movimiento_inventario",
                    registro_id=movimiento.id_movimiento,
                    descripcion=f"Movimiento {movimiento.tipo} del producto {producto.codigo_producto} por cantidad {movimiento.cantidad}. Motivo: {movimiento.motivo}"
                )

            flash('Materia prima actualizada correctamente', 'success')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar materia prima: {str(e)}', 'danger')

    return redirect(url_for('materias_primas_bp.listado_productos'))


@materias_primas_bp.route('/materias-primas/eliminar', methods=['GET', 'POST'])
def eliminar_producto():
    producto_form = forms.ProductoForm()

    marcas = Marca.query.filter(Marca.estatus == 'ACTIVO').all()
    unidades = UnidadMedida.query.all()

    producto_form.id_marca.choices = [(m.id_marca, m.nombre_marca) for m in marcas]
    producto_form.id_unidad_medida.choices = [(u.id_unidad_medida, u.nombre_unidad) for u in unidades]

    producto = None

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == codigo_producto
        ).first()

        if not producto:
            flash('Materia prima no encontrada', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        producto_form.codigo_producto.data = producto.codigo_producto
        producto_form.nombre.data = producto.nombre
        producto_form.stock_actual.data = producto.stock_actual
        producto_form.precio_compra.data = producto.precio_compra
        producto_form.precio_unitario.data = producto.precio_unitario
        producto_form.estatus.data = producto.estatus
        producto_form.id_marca.data = producto.id_marca
        producto_form.id_unidad_medida.data = producto.id_unidad_medida
        producto_form.stock_minimo.data = inventario.stock_minimo if inventario else 0
        producto_form.stock_maximo.data = inventario.stock_maximo if inventario else 0

    if request.method == 'POST':
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == producto_form.codigo_producto.data
        ).first()

        if producto:
            try:
                producto.estatus = 'INACTIVO'
                db.session.commit()

                registrar_log(
                    session.get('user_id', 0),
                    "BAJA_MATERIA_PRIMA",
                    tabla="producto",
                    registro_id=0,
                    descripcion=f"Se cambió a INACTIVO la materia prima {producto.nombre} con código {producto.codigo_producto}"
                )

                flash('Materia prima desactivada correctamente', 'warning')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al desactivar materia prima: {str(e)}', 'danger')

        return redirect(url_for('materias_primas_bp.listado_productos'))

    return render_template(
        'materias_primas/eliminar_producto.html',
        form=producto_form,
        producto=producto,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/movimiento', methods=['GET', 'POST'])
def registrar_movimiento():
    movimiento_form = forms.MovimientoInventarioForm()

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == codigo_producto
        ).first()

        if not producto:
            flash('Materia prima no encontrada', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        movimiento_form.codigo_producto.data = producto.codigo_producto

        return render_template(
            'materias_primas/movimiento_form.html',
            form=movimiento_form,
            producto=producto,
            active_page='inventario'
        )

    if movimiento_form.validate_on_submit():
        producto = db.session.query(Producto).filter(
            Producto.codigo_producto == movimiento_form.codigo_producto.data
        ).first()

        if not producto:
            flash('Materia prima no encontrada', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        cantidad = movimiento_form.cantidad.data

        try:
            if movimiento_form.tipo.data == 'ENTRADA':
                producto.stock_actual += cantidad
            elif movimiento_form.tipo.data == 'SALIDA':
                if producto.stock_actual < cantidad:
                    flash('No hay suficiente stock para registrar la salida', 'danger')
                    return redirect(url_for('materias_primas_bp.registrar_movimiento', codigo=producto.codigo_producto))
                producto.stock_actual -= cantidad
            elif movimiento_form.tipo.data == 'AJUSTE':
                producto.stock_actual = cantidad

            movimiento = MovimientoInventario(
                codigo_producto=producto.codigo_producto,
                tipo=movimiento_form.tipo.data,
                cantidad=cantidad,
                motivo=movimiento_form.motivo.data
            )

            db.session.add(movimiento)
            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "MOVIMIENTO_INVENTARIO",
                tabla="movimiento_inventario",
                registro_id=movimiento.id_movimiento,
                descripcion=f"Movimiento {movimiento.tipo} del producto {producto.codigo_producto} por cantidad {movimiento.cantidad}. Motivo: {movimiento.motivo}"
            )

            flash('Movimiento registrado correctamente', 'success')
            return redirect(url_for('materias_primas_bp.detalle_producto', codigo=producto.codigo_producto))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar movimiento: {str(e)}', 'danger')

    return redirect(url_for('materias_primas_bp.listado_productos'))