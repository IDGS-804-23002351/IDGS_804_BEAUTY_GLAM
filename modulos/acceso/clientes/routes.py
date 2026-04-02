from . import clientes
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text 

# --- READ (LISTAR) ---
@clientes.route("/clientes", methods=['GET'])
def indexClientes():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', 'ACTIVO')
    
    try:
        query = text("CALL sp_listar_clientes(:estatus, :buscar)")
        result = db.session.execute(query, {"estatus": estatus, "buscar": buscar})
        lista_clientes = result.fetchall()
        
        create_form = forms.ClienteForm() 
        return render_template("clientes/listadoclientes.html",
                             form=create_form, 
                             clientes=lista_clientes)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('acceso.login'))

# --- FORMULARIO (CREAR Y EDITAR) ---
@clientes.route("/clientes/nuevo", methods=['GET'])
def nuevo_cliente():
    form = forms.ClienteForm()
    return render_template("clientes/formclientes.html", form=form, accion='crear')

@clientes.route("/clientes/editar/<int:id>", methods=['GET'])
def editar_cliente(id):
    try:
        # Obtener datos del cliente
        query = text("CALL sp_obtener_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        cliente_data = result.fetchone()
        
        if not cliente_data:
            flash("Cliente no encontrado", "danger")
            return redirect(url_for('clientes.indexClientes'))
        
        # Crear formulario y llenar con datos
        form = forms.ClienteForm()
        form.id.data = cliente_data.id_cliente
        form.nombre.data = cliente_data.nombre_persona
        form.apellidos.data = cliente_data.apellidos
        form.telefono.data = cliente_data.telefono
        form.correo.data = cliente_data.correo
        form.direccion.data = cliente_data.direccion
        form.nombre_usuario.data = cliente_data.nombre_usuario
        form.estatus.data = cliente_data.estatus_cliente
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='editar',
                             cliente=cliente_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))

# --- CREATE (CREAR) ---
@clientes.route("/clientes/crear", methods=['POST'])
def crear_cliente():
    form = forms.ClienteForm(request.form)
    if form.validate_on_submit():
        try:
            query = text("""
                CALL sp_crear_cliente(
                    :nombre, :apellidos, :telefono, :correo, 
                    :direccion, :nombre_usuario, :contrasenia
                )
            """)
            
            db.session.execute(query, {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "telefono": form.telefono.data,
                "correo": form.correo.data,
                "direccion": form.direccion.data,
                "nombre_usuario": form.nombre_usuario.data,  
                "contrasenia": form.contrasenia.data       
            })
            db.session.commit()
            flash("Cliente registrado exitosamente", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            
    return redirect(url_for('clientes.indexClientes'))

# --- UPDATE (ACTUALIZAR) ---
@clientes.route("/clientes/actualizar/<int:id>", methods=['POST'])
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
            "estatus": form.estatus.data
        })
        db.session.commit()
        flash("Cliente actualizado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        
    return redirect(url_for('clientes.indexClientes'))

# --- DELETE (BORRADO LÓGICO) ---
@clientes.route("/clientes/eliminar/<int:id>", methods=['POST'])
def eliminar_cliente(id):
    try:
        print(f"=== ELIMINANDO CLIENTE ID: {id} ===")
        
        query = text("CALL sp_eliminar_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        db.session.commit()
        
        print("Eliminación exitosa")
        flash("Cliente desactivado correctamente", "warning")
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {str(e)}")
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        
    return redirect(url_for('clientes.indexClientes'))
# --- VER CLIENTE ---
@clientes.route("/clientes/ver/<int:id>", methods=['GET'])
def ver_cliente(id):
    try:
        query = text("CALL sp_obtener_cliente(:id)")
        result = db.session.execute(query, {"id": id})
        cliente_data = result.fetchone()
        
        if not cliente_data:
            flash("Cliente no encontrado", "danger")
            return redirect(url_for('clientes.indexClientes'))
        
        form = forms.ClienteForm()
        form.id.data = cliente_data.id_cliente
        form.nombre.data = cliente_data.nombre_persona
        form.apellidos.data = cliente_data.apellidos
        form.telefono.data = cliente_data.telefono
        form.correo.data = cliente_data.correo
        form.direccion.data = cliente_data.direccion
        form.nombre_usuario.data = cliente_data.nombre_usuario
        form.estatus.data = cliente_data.estatus_cliente
        
        return render_template("clientes/formclientes.html", 
                             form=form, 
                             accion='ver',
                             cliente=cliente_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('clientes.indexClientes'))