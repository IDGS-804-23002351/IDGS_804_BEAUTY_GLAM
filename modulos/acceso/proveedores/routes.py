from . import proveedor
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db
from sqlalchemy import text

# --- READ (LISTAR) ---
@proveedor.route("/proveedores", methods=['GET'])
def indexProveedores():
    buscar = request.args.get('buscar', None)
    estatus = request.args.get('estatus', None)
    id_tipo_proveedor = request.args.get('id_tipo_proveedor', None)
    
    try:
        query = text("CALL sp_listar_proveedores(:estatus, :id_tipo_proveedor, :buscar)")
        result = db.session.execute(query, {
            "estatus": estatus if estatus else None,
            "id_tipo_proveedor": int(id_tipo_proveedor) if id_tipo_proveedor and id_tipo_proveedor != '' else None,
            "buscar": buscar if buscar else None
        })
        lista_proveedores = result.fetchall()
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        create_form = forms.ProveedorForm()
        filtro_form = forms.FiltroProveedorForm()
        
        filtro_form.id_tipo_proveedor.choices = [('', 'Todos')] + [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        create_form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        return render_template("proveedores/listadoProveedores.html",
                             form=create_form,
                             filtro=filtro_form,
                             proveedores=lista_proveedores)
    except Exception as e:
        flash(f"Error al listar: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- FORMULARIO NUEVO PROVEEDOR ---
@proveedor.route("/proveedores/nuevo", methods=['GET'])
def nuevo_proveedor():
    form = forms.ProveedorForm()
    try:
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        # IMPORTANTE: limpiar choices antes de asignar
        form.id_tipo_proveedor.choices = []
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        print(f"Tipos cargados: {form.id_tipo_proveedor.choices}")  # Para depurar
    except Exception as e:
        print(f"Error cargando tipos: {e}")
        form.id_tipo_proveedor.choices = []
    return render_template("proveedores/formproveedores.html", form=form, accion='crear')
# --- CREATE (CREAR) ---
@proveedor.route("/proveedores/crear", methods=['POST'])
def crear_proveedor():
    form = forms.ProveedorForm(request.form)
    
    print("=== CREANDO PROVEEDOR ===")
    print(f"Datos recibidos: {request.form}")
    
    try:
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
    except:
        pass
    
    print(f"Formulario válido: {form.validate_on_submit()}")
    if not form.validate_on_submit():
        print(f"Errores en el formulario: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
                print(f"Error en {field}: {error}")
    else:
        print("Formulario validado correctamente")
        print(f"Nombre: {form.nombre.data}")
        print(f"Apellidos: {form.apellidos.data}")
        print(f"Teléfono: {form.telefono.data}")
        print(f"Correo: {form.correo.data}")
        print(f"Dirección: {form.direccion.data}")
        print(f"RFC Empresa: {form.rfc_empresa.data}")
        print(f"Tipo Proveedor: {form.id_tipo_proveedor.data}")
        
        try:
            query = text("""
                CALL sp_crear_proveedor(
                    :nombre, :apellidos, :telefono, :correo, 
                    :direccion, :rfc_empresa, :id_tipo_proveedor
                )
            """)
            
            db.session.execute(query, {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "telefono": form.telefono.data,
                "correo": form.correo.data,
                "direccion": form.direccion.data,
                "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
                "id_tipo_proveedor": form.id_tipo_proveedor.data
            })
            db.session.commit()
            print("SP ejecutado correctamente")
            flash("Proveedor registrado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR EN SP: {str(e)}")
            flash(f"Error: {str(e)}", "danger")
            
    return redirect(url_for('proveedor.indexProveedores'))

# --- VER PROVEEDOR ---
@proveedor.route("/proveedores/ver/<int:id>", methods=['GET'])
def ver_proveedor(id):
    try:
        query = text("CALL sp_obtener_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        proveedor_data = result.fetchone()
        
        if not proveedor_data:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('proveedor.indexProveedores'))
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        form = forms.ProveedorForm()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        form.estatus.data = proveedor_data.estatus_proveedor
        
        return render_template("proveedores/formproveedores.html", 
                             form=form, 
                             accion='ver',
                             proveedor=proveedor_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('proveedor.indexProveedores'))

# --- EDITAR PROVEEDOR ---
@proveedor.route("/proveedores/editar/<int:id>", methods=['GET'])
def editar_proveedor(id):
    try:
        query = text("CALL sp_obtener_proveedor(:id)")
        result = db.session.execute(query, {"id": id})
        proveedor_data = result.fetchone()
        
        if not proveedor_data:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('proveedor.indexProveedores'))
        
        tipos_query = text("CALL sp_listar_tipos_proveedor()")
        tipos_result = db.session.execute(tipos_query)
        tipos_proveedor = tipos_result.fetchall()
        
        form = forms.ProveedorForm()
        form.id_tipo_proveedor.choices = [(t.id_tipo_proveedor, t.tipo_proveedor) for t in tipos_proveedor]
        
        form.nombre.data = proveedor_data.nombre_persona
        form.apellidos.data = proveedor_data.apellidos
        form.telefono.data = proveedor_data.telefono
        form.correo.data = proveedor_data.correo
        form.direccion.data = proveedor_data.direccion
        form.rfc_empresa.data = proveedor_data.rfc_empresa
        form.id_tipo_proveedor.data = proveedor_data.id_tipo_proveedor
        form.estatus.data = proveedor_data.estatus_proveedor
        
        return render_template("proveedores/formproveedores.html", 
                             form=form, 
                             accion='editar',
                             proveedor=proveedor_data)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('proveedor.indexProveedores'))

# --- UPDATE (ACTUALIZAR) ---
@proveedor.route("/proveedores/actualizar/<int:id>", methods=['POST'])
def actualizar_proveedor(id):
    form = forms.ProveedorForm(request.form)
    
    try:
        query = text("""
            CALL sp_actualizar_proveedor(
                :id, :nombre, :apellidos, :telefono, 
                :correo, :direccion, :rfc_empresa, :id_tipo_proveedor, :estatus
            )
        """)
        db.session.execute(query, {
            "id": id,
            "nombre": form.nombre.data,
            "apellidos": form.apellidos.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "rfc_empresa": form.rfc_empresa.data if form.rfc_empresa.data else None,
            "id_tipo_proveedor": form.id_tipo_proveedor.data,
            "estatus": form.estatus.data
        })
        db.session.commit()
        flash("Proveedor actualizado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))

# --- DELETE (BORRADO LÓGICO) ---
@proveedor.route("/proveedores/eliminar/<int:id>", methods=['POST'])
def eliminar_proveedor(id):
    try:
        query = text("CALL sp_eliminar_proveedor(:id)")
        db.session.execute(query, {"id": id})
        db.session.commit()
        flash("Proveedor desactivado correctamente", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        
    return redirect(url_for('proveedor.indexProveedores'))