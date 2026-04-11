import os
from uuid import uuid4
from werkzeug.utils import secure_filename

from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required

from . import materias_primas_bp
import forms
from models import db
from models import (
    Producto, Marca, UnidadMedida, InventarioProducto,
    MovimientoInventario, Proveedor, Persona, Usuario, registrar_log
)


def es_proveedor():
    rol = session.get('user_rol', '')
    return rol.upper() == 'PROVEEDOR'


def obtener_proveedor_sesion():
    id_usuario = session.get('user_id')

    if not id_usuario:
        return None

    proveedor = db.session.query(Proveedor).join(
        Persona, Proveedor.id_persona == Persona.id_persona
    ).join(
        Usuario, Usuario.id_persona == Persona.id_persona
    ).filter(
        Usuario.id_usuario == id_usuario
    ).first()

    return proveedor


def obtener_query_productos_filtrada():
    query = db.session.query(Producto).join(Marca)

    if es_proveedor():
        proveedor = obtener_proveedor_sesion()

        if not proveedor:
            return query.filter(False)

        query = query.filter(Marca.rfc == proveedor.rfc)

    return query


def obtener_producto_filtrado_por_sesion(codigo_producto):
    return obtener_query_productos_filtrada().filter(
        Producto.codigo_producto == codigo_producto
    ).first()


def guardar_foto_producto(archivo):
    if not archivo or archivo.filename == '':
        return None

    nombre_seguro = secure_filename(archivo.filename)
    extension = os.path.splitext(nombre_seguro)[1]
    nuevo_nombre = f"{uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, 'uploads', 'materias_primas')
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_completa = os.path.join(carpeta_destino, nuevo_nombre)
    archivo.save(ruta_completa)

    return f"uploads/materias_primas/{nuevo_nombre}"


def generar_alerta_stock(producto):
    inventario = db.session.query(InventarioProducto).filter(
        InventarioProducto.codigo_producto == producto.codigo_producto
    ).first()

    if not inventario:
        return None

    stock_actual = producto.stock_actual if producto.stock_actual is not None else 0
    stock_minimo = inventario.stock_minimo if inventario.stock_minimo is not None else 0
    stock_maximo = inventario.stock_maximo if inventario.stock_maximo is not None else 0

    if stock_actual <= stock_minimo:
        return {
            'tipo': 'warning',
            'mensaje': (
                f'Alerta: la materia prima "{producto.nombre}" está en stock mínimo o por debajo de él. '
                f'Stock actual: {stock_actual}. Stock mínimo: {stock_minimo}.'
            )
        }

    if stock_maximo > 0 and stock_actual > stock_maximo:
        return {
            'tipo': 'warning',
            'mensaje': (
                f'Alerta: la materia prima "{producto.nombre}" superó el stock máximo permitido. '
                f'Stock actual: {stock_actual}. Stock máximo: {stock_maximo}.'
            )
        }

    return None
def obtener_alertas_stock_global():
    alertas = []

    productos = db.session.query(Producto).all()

    for producto in productos:
        alerta = generar_alerta_stock(producto)
        if alerta:
            alertas.append(alerta)

    return alertas

@materias_primas_bp.route('/materias-primas', methods=['GET', 'POST'])
@login_required
def listado_productos():
    filtro_form = forms.FiltroProductoForm()

    if es_proveedor():
        proveedor = obtener_proveedor_sesion()

        if not proveedor:
            flash('No se encontró el proveedor asociado a tu usuario', 'danger')
            return redirect(url_for('acceso.dashboard'))

        marcas = Marca.query.filter(
            Marca.rfc == proveedor.rfc
        ).all()
    else:
        marcas = Marca.query.all()

    unidades = UnidadMedida.query.all()

    filtro_form.id_marca.choices = [(0, 'Todas')] + [
        (m.id_marca, m.nombre_marca) for m in marcas
    ]

    filtro_form.id_unidad_medida.choices = [(0, 'Todas')] + [
        (u.id_unidad_medida, u.nombre_unidad) for u in unidades
    ]

    query = obtener_query_productos_filtrada()

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
@login_required
def nuevo_producto():
    if es_proveedor():
        flash('No tienes permiso para registrar productos.', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

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

        archivo_foto = request.files.get('foto')
        ruta_foto = guardar_foto_producto(archivo_foto)

        nuevo_producto = Producto(
            codigo_producto=producto_form.codigo_producto.data,
            nombre=producto_form.nombre.data,
            foto=ruta_foto,
            stock_actual=0,
            precio_compra=0,
            precio_unitario=0,
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

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "ALTA_MATERIA_PRIMA",
                tabla="producto",
                registro_id=0,
                descripcion=f"Se registró la materia prima {nuevo_producto.nombre} con código {nuevo_producto.codigo_producto}"
            )

            flash('Materia prima registrada correctamente con stock inicial en 0. Debes registrar una compra para ingresar existencias.', 'success')
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
@login_required
def detalle_producto():
    codigo_producto = request.args.get('codigo')
    producto = obtener_producto_filtrado_por_sesion(codigo_producto)

    if not producto:
        flash('Materia prima no encontrada o no tienes permiso para verla', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

    inventario = db.session.query(InventarioProducto).filter(
        InventarioProducto.codigo_producto == producto.codigo_producto
    ).first()

    movimientos = db.session.query(MovimientoInventario).filter(
        MovimientoInventario.codigo_producto == producto.codigo_producto
    ).order_by(MovimientoInventario.fecha.desc()).all()

    alerta_stock = generar_alerta_stock(producto)

    return render_template(
        'materias_primas/detalle_producto.html',
        producto=producto,
        inventario=inventario,
        movimientos=movimientos,
        alerta_stock=alerta_stock,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/editar', methods=['GET', 'POST'])
@login_required
def editar_producto():
    if es_proveedor():
        flash('No tienes permiso para editar productos.', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

    producto_form = forms.ProductoForm()

    marcas = Marca.query.filter(Marca.estatus == 'ACTIVO').all()
    unidades = UnidadMedida.query.all()

    producto_form.id_marca.choices = [(m.id_marca, m.nombre_marca) for m in marcas]
    producto_form.id_unidad_medida.choices = [(u.id_unidad_medida, u.nombre_unidad) for u in unidades]

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = obtener_producto_filtrado_por_sesion(codigo_producto)

        if not producto:
            flash('Materia prima no encontrada o no tienes permiso para editarla', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        producto_form.codigo_producto.data = producto.codigo_producto
        producto_form.nombre.data = producto.nombre
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
        producto = obtener_producto_filtrado_por_sesion(producto_form.codigo_producto.data)

        if not producto:
            flash('Materia prima no encontrada o no tienes permiso para editarla', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        archivo_foto = request.files.get('foto')
        ruta_foto = guardar_foto_producto(archivo_foto)

        try:
            producto.nombre = producto_form.nombre.data
            producto.estatus = producto_form.estatus.data
            producto.id_marca = producto_form.id_marca.data
            producto.id_unidad_medida = producto_form.id_unidad_medida.data

            if ruta_foto:
                producto.foto = ruta_foto

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

            db.session.commit()

            registrar_log(
                session.get('user_id', 0),
                "EDICION_MATERIA_PRIMA",
                tabla="producto",
                registro_id=0,
                descripcion=f"Se modificó la materia prima {producto.nombre} con código {producto.codigo_producto}"
            )

            flash('Materia prima actualizada correctamente', 'success')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar materia prima: {str(e)}', 'danger')

    return redirect(url_for('materias_primas_bp.listado_productos'))


@materias_primas_bp.route('/materias-primas/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_producto():
    if es_proveedor():
        flash('No tienes permiso para eliminar productos.', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

    producto_form = forms.ProductoForm()

    marcas = Marca.query.filter(Marca.estatus == 'ACTIVO').all()
    unidades = UnidadMedida.query.all()

    producto_form.id_marca.choices = [(m.id_marca, m.nombre_marca) for m in marcas]
    producto_form.id_unidad_medida.choices = [(u.id_unidad_medida, u.nombre_unidad) for u in unidades]

    producto = None

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = obtener_producto_filtrado_por_sesion(codigo_producto)

        if not producto:
            flash('Materia prima no encontrada o no tienes permiso para eliminarla', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        inventario = db.session.query(InventarioProducto).filter(
            InventarioProducto.codigo_producto == producto.codigo_producto
        ).first()

        producto_form.codigo_producto.data = producto.codigo_producto
        producto_form.nombre.data = producto.nombre
        producto_form.estatus.data = producto.estatus
        producto_form.id_marca.data = producto.id_marca
        producto_form.id_unidad_medida.data = producto.id_unidad_medida
        producto_form.stock_minimo.data = inventario.stock_minimo if inventario else 0
        producto_form.stock_maximo.data = inventario.stock_maximo if inventario else 0

    if request.method == 'POST':
        producto = obtener_producto_filtrado_por_sesion(producto_form.codigo_producto.data)

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
        else:
            flash('Materia prima no encontrada o no tienes permiso para eliminarla', 'danger')

        return redirect(url_for('materias_primas_bp.listado_productos'))

    return render_template(
        'materias_primas/eliminar_producto.html',
        form=producto_form,
        producto=producto,
        active_page='inventario'
    )


@materias_primas_bp.route('/materias-primas/movimiento', methods=['GET', 'POST'])
@login_required
def registrar_movimiento():
    if es_proveedor():
        flash('No tienes permiso para registrar movimientos de inventario.', 'danger')
        return redirect(url_for('materias_primas_bp.listado_productos'))

    movimiento_form = forms.MovimientoInventarioForm()

    if request.method == 'GET':
        codigo_producto = request.args.get('codigo')
        producto = obtener_producto_filtrado_por_sesion(codigo_producto)

        if not producto:
            flash('Materia prima no encontrada o no tienes permiso para mover inventario', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        movimiento_form.codigo_producto.data = producto.codigo_producto

        return render_template(
            'materias_primas/movimiento_form.html',
            form=movimiento_form,
            producto=producto,
            active_page='inventario'
        )

    if movimiento_form.validate_on_submit():
        producto = obtener_producto_filtrado_por_sesion(movimiento_form.codigo_producto.data)

        if not producto:
            flash('Materia prima no encontrada o no tienes permiso para mover inventario', 'danger')
            return redirect(url_for('materias_primas_bp.listado_productos'))

        cantidad = movimiento_form.cantidad.data

        try:
            if movimiento_form.tipo.data == 'ENTRADA':
                producto.stock_actual += cantidad

                if hasattr(movimiento_form, 'precio_compra') and movimiento_form.precio_compra.data is not None:
                    producto.precio_compra = movimiento_form.precio_compra.data

                motivo_movimiento = movimiento_form.motivo.data or 'Compra de materia prima'

            elif movimiento_form.tipo.data == 'SALIDA':
                if producto.stock_actual < cantidad:
                    flash('No hay suficiente stock para registrar la salida', 'danger')
                    return redirect(url_for('materias_primas_bp.registrar_movimiento', codigo=producto.codigo_producto))
                producto.stock_actual -= cantidad
                motivo_movimiento = movimiento_form.motivo.data

            elif movimiento_form.tipo.data == 'AJUSTE':
                producto.stock_actual = cantidad
                motivo_movimiento = movimiento_form.motivo.data

            movimiento = MovimientoInventario(
                codigo_producto=producto.codigo_producto,
                tipo=movimiento_form.tipo.data,
                cantidad=cantidad,
                motivo=motivo_movimiento
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

            alerta_stock = generar_alerta_stock(producto)
            if alerta_stock:
                flash(alerta_stock['mensaje'], alerta_stock['tipo'])

            return redirect(url_for('materias_primas_bp.detalle_producto', codigo=producto.codigo_producto))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar movimiento: {str(e)}', 'danger')

    return redirect(url_for('materias_primas_bp.listado_productos'))