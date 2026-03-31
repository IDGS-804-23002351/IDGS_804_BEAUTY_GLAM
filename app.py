from flask import Flask, render_template, request, redirect, url_for, flash
from forms import UserForm

app = Flask(__name__)
app.secret_key = "123456"


# =========================
# LOGIN / INICIO / LOGOUT
# =========================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')

        # Login simple temporal
        if usuario and password:
            flash('Inicio de sesión correcto', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Revisa tus credenciales', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def inicio():
    return render_template(
        'dashboard.html',
        active_page='dashboard'
    )


@app.route('/logout')
def logout():
    flash('Sesión cerrada', 'success')
    return redirect(url_for('login'))


# =========================
# USUARIOS
# =========================
@app.route('/usuarios')
def listado_usuarios():
    return render_template(
        'usuarios/listado.html',
        active_page='usuarios'
    )


@app.route('/usuarios/form', methods=['GET', 'POST'])
def usuarios_form():
    form = UserForm()

    if request.method == 'POST':
        if form.validate():
            flash('Formulario válido', 'success')
            return redirect(url_for('usuarios_listado'))
        else:
            flash('Revisa los campos', 'danger')

    return render_template(
        'usuarios/form.html',
        form=form,
        active_page='usuarios'
    )


# =========================
# ROLES
# =========================
@app.route('/roles')
def listado_roles():
    return render_template(
        'roles/listadoroles.html',
        active_page='roles'
    )


@app.route('/roles/form', methods=['GET', 'POST'])
def roles_form():
    if request.method == 'POST':
        flash('Rol guardado correctamente', 'success')
        return redirect(url_for('roles_listado'))

    return render_template(
        'roles/formroles.html',
        active_page='roles'
    )


# =========================
# PRODUCTOS
# =========================
@app.route('/productos')
def listado_productos():
    return render_template(
        'productos/listadoproductos.html',
        active_page='productos'
    )


@app.route('/productos/form', methods=['GET', 'POST'])
def productos_form():
    if request.method == 'POST':
        flash('Producto guardado correctamente', 'success')
        return redirect(url_for('productos_listado'))

    return render_template(
        'productos/formproductos.html',
        active_page='productos'
    )


# =========================
# CLIENTES
# =========================
@app.route('/clientes')
def listado_clientes():
    return render_template(
        'clientes/listadoclientes.html',
        active_page='clientes'
    )


@app.route('/clientes/form', methods=['GET', 'POST'])
def clientes_form():
    if request.method == 'POST':
        flash('Cliente guardado correctamente', 'success')
        return redirect(url_for('clientes_listado'))

    return render_template(
        'clientes/formclientes.html',
        active_page='clientes'
    )


# =========================
# EMPLEADOS
# =========================
@app.route('/empleados')
def listado_empleados():
    return render_template(
        'empleados/listadoempleados.html',
        active_page='empleados'
    )


@app.route('/empleados/form', methods=['GET', 'POST'])
def empleados_form():
    if request.method == 'POST':
        flash('Empleado guardado correctamente', 'success')
        return redirect(url_for('empleados_listado'))

    return render_template(
        'empleados/formempleados.html',
        active_page='empleados'
    )


# =========================
# CITAS
# =========================
@app.route('/citas')
def listado_citas():
    return render_template(
        'citas/listadocitas.html',
        active_page='citas'
    )


@app.route('/citas/form', methods=['GET', 'POST'])
def citas_form():
    if request.method == 'POST':
        flash('Cita guardada correctamente', 'success')
        return redirect(url_for('citas_listado'))

    return render_template(
        'citas/formcitas.html',
        active_page='citas'
    )


# =========================
# INVENTARIO
# =========================
@app.route('/inventario')
def listado_inventario():
    return render_template(
        'inventario/listadoinventario.html',
        active_page='inventario'
    )


@app.route('/inventario/form', methods=['GET', 'POST'])
def inventario_form():
    if request.method == 'POST':
        flash('Insumo guardado correctamente', 'success')
        return redirect(url_for('inventario_listado'))

    return render_template(
        'inventario/forminventario.html',
        active_page='inventario'
    )


# =========================
# SERVICIOS
# =========================
@app.route('/servicios')
def listado_servicios():
    return render_template(
        'servicios/listadoservicios.html',
        active_page='servicios'
    )


@app.route('/servicios/form', methods=['GET', 'POST'])
def servicios_form():
    if request.method == 'POST':
        flash('Servicio guardado correctamente', 'success')
        return redirect(url_for('servicios_listado'))

    return render_template(
        'servicios/formservicios.html',
        active_page='servicios'
    )


# =========================
# CONSUMO
# =========================
@app.route('/consumo')
def listado_consumo():
    return render_template(
        'consumo/listadoconsumo.html',
        active_page='consumo'
    )


@app.route('/consumo/form', methods=['GET', 'POST'])
def consumo_form():
    if request.method == 'POST':
        flash('Consumo guardado correctamente', 'success')
        return redirect(url_for('consumo_listado'))

    return render_template(
        'consumo/formconsumo.html',
        active_page='consumo'
    )


# =========================
# PAGOS
# =========================
@app.route('/pagos')
def listado_pagos():
    return render_template(
        'pagos/listadopagos.html',
        active_page='pagos'
    )


@app.route('/pagos/form', methods=['GET', 'POST'])
def pagos_form():
    if request.method == 'POST':
        flash('Pago registrado correctamente', 'success')
        return redirect(url_for('pagos_listado'))

    return render_template(
        'pagos/formpagos.html',
        active_page='pagos'
    )


# =========================
# PROMOS
# =========================
@app.route('/promos')
def listado_promos():
    return render_template(
        'promos/listadopromos.html',
        active_page='promos'
    )


@app.route('/promos/form', methods=['GET', 'POST'])
def promos_form():
    if request.method == 'POST':
        flash('Promoción guardada correctamente', 'success')
        return redirect(url_for('promos_listado'))

    return render_template(
        'promos/formpromos.html',
        active_page='promos'
    )


# =========================
# PROVEEDORES
# =========================
@app.route('/proveedores')
def listado_proveedores():
    return render_template(
        'proveedores/listadoproveedores.html',
        active_page='proveedores'
    )


@app.route('/proveedores/form', methods=['GET', 'POST'])
def proveedores_form():
    if request.method == 'POST':
        flash('Proveedor guardado correctamente', 'success')
        return redirect(url_for('proveedores_listado'))

    return render_template(
        'proveedores/formproveedores.html',
        active_page='proveedores'
    )


# =========================
# REPORTES
# =========================
@app.route('/reportes')
def listado_reportes():
    return render_template(
        'reportes/listadoreportes.html',
        active_page='reportes'
    )


@app.route('/reportes/form', methods=['GET', 'POST'])
def reportes_form():
    if request.method == 'POST':
        flash('Reporte generado correctamente', 'success')
        return redirect(url_for('reportes_listado'))

    return render_template(
        'reportes/formreportes.html',
        active_page='reportes'
    )


# =========================
# BITACORA
# =========================
@app.route('/bitacora')
def listado_bitacora():
    return render_template(
        'bitacora/listadobitacora.html',
        active_page='bitacora'
    )


@app.route('/bitacora/detalle')
def bitacora_detalle():
    
	return render_template(
        'bitacora/detallebitacora.html',
        active_page='bitacora'
    )


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)