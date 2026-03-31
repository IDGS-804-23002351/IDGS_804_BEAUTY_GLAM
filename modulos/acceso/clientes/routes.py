from . import cliente 
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text 

# --- READ (LISTAR) ---
@cliente.route("/clientes", methods=['GET'])
def indexClientes():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', 'ACTIVO')
    
    try:
        query = text("CALL sp_listar_clientes(:estatus, :buscar)")
        result = db.session.execute(query, {"estatus": estatus, "buscar": buscar})
        lista_clientes = result.fetchall()
        
        create_form = forms.ClienteForm() 
        return render_template("clientes/listadoCursos.html",
                             form=create_form, 
                             clientes=lista_clientes)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- CREATE (CREAR) ---
@cliente.route("/clientes/crear", methods=['POST'])
def crear_cliente():
    form = forms.ClienteForm(request.form)
    if form.validate_on_submit():
        try:
            query = text("""
                CALL sp_crear_cliente(
                    :nombre, :apellidos, :telefono, :correo, 
                    :direccion, :usuario, :password
                )
            """)
            
            db.session.execute(query, {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "telefono": form.telefono.data,
                "correo": form.correo.data,
                "direccion": form.direccion.data,
                "usuario": form.usuario.data,
                "password": form.password.data 
            })
            db.session.commit()
            flash("Cliente registrado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            
    return redirect(url_for('cliente.indexClientes'))

# --- UPDATE (ACTUALIZAR) ---
@cliente.route("/clientes/actualizar/<int:id>", methods=['POST'])
def actualizar_cliente(id):
    form = forms.ClienteForm(request.form)
    try:
        query = text("""
            CALL sp_actualizar_cliente(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :estatus
            )
        """)
        db.session.execute(query, {
            "id": id,
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "estatus": request.form.get('estatus', 'ACTIVO')
        })
        db.session.commit()
        flash("Datos actualizados", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        
    return redirect(url_for('cliente.indexClientes'))

# --- DELETE (BORRADO LÓGICO) ---
@cliente.route("/clientes/eliminar/<int:id>", methods=['POST'])
def eliminar_cliente(id):
    try:
        query = text("CALL sp_eliminar_cliente(:id)")
        db.session.execute(query, {"id": id})
        db.session.commit()
        flash("Cliente desactivado correctamente", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        
    return redirect(url_for('cliente.indexClientes'))