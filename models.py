from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from config import bitacora_mongo
from flask import request 

from flask import request 
from datetime import datetime
from config import bitacora_mongo, historial_clientes_mongo

db = SQLAlchemy()

def registrar_log(usuario_id, accion, modulo=None, detalle=None, tabla=None, registro_id=None, descripcion=None):

    mx_tz = pytz.timezone('America/Mexico_City')
    fecha_actual = datetime.now(mx_tz)
    
    tabla_final = modulo or tabla or "General"
    desc_final = detalle or descripcion or "Sin detalle"


    log = {
        "id_usuario": usuario_id,
        "accion": accion,
        "tabla_afectada": tabla_final,  
        "id_registro": registro_id,
        "descripcion": desc_final,     
        "fecha_hora": fecha_actual,
        "ip": request.remote_addr if request else "127.0.0.1"
    }

    try:
        bitacora_mongo.insert_one(log)
    except Exception as e:
        print(f"Error al guardar en MongoDB: {e}")
def registrar_historial_cliente(usuario_id, cliente_id, accion, detalle, datos_anteriores=None, datos_nuevos=None):
    """
    Registra el historial específico de clientes en MongoDB
    """
    mx_tz = pytz.timezone('America/Mexico_City')
    fecha_actual = datetime.now(mx_tz)
    
    historial = {
        "id_cliente": cliente_id,
        "id_usuario": usuario_id,
        "accion": accion,  # CREAR, ACTUALIZAR, ELIMINAR, VER, etc.
        "detalle": detalle,
        "datos_anteriores": datos_anteriores,
        "datos_nuevos": datos_nuevos,
        "fecha_hora": fecha_actual,
        "ip": request.remote_addr if request else "127.0.0.1"
    }
    
    try:
        historial_clientes_mongo.insert_one(historial)
        return True
    except Exception as e:
        print(f"Error al guardar historial de cliente: {e}")
        return False

def obtener_historial_cliente(cliente_id, limite=50, offset=0):
    """
    Obtiene el historial de un cliente específico desde MongoDB
    """
    try:
        historial = historial_clientes_mongo.find(
            {"id_cliente": cliente_id}
        ).sort("fecha_hora", -1).skip(offset).limit(limite)
        
        # Convertir ObjectId a string para JSON
        historial_list = []
        for item in historial:
            item['_id'] = str(item['_id'])
            historial_list.append(item)
        
        # Contar total
        total = historial_clientes_mongo.count_documents({"id_cliente": cliente_id})
        
        return historial_list, total
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return [], 0
class Persona(db.Model):
    __tablename__ = 'persona'
    id_persona = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_persona = db.Column(db.String(50))
    apellidos = db.Column(db.String(100)) # Corregido a plural para empatar con SQL
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(150))
    direccion = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.Date)
    genero = db.Column(db.Enum('Femenino', 'Masculino', 'Otro', 'Sin especificar'), default='Sin especificar')
    ultima_actualizacion = db.Column(db.DateTime)

    usuarios = db.relationship('Usuario', back_populates='persona')
    clientes = db.relationship('Cliente', back_populates='persona')
    empleados = db.relationship('Empleado', back_populates='persona')
    proveedores = db.relationship('Proveedor', back_populates='persona')

class Empresa(db.Model):
    __tablename__ = 'empresa'
    rfc = db.Column(db.String(13), primary_key=True)
    nombre_empresa = db.Column(db.String(150))
    direccion = db.Column(db.String(255))
    contacto = db.Column(db.String(150))

    marcas = db.relationship('Marca', back_populates='empresa')
    proveedores = db.relationship('Proveedor', back_populates='empresa')

class RolPermiso(db.Model):
    __tablename__ = 'rol_permiso'
    id_rol_permiso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id_permisos'))
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulo.id_modulo'))

class Modulo(db.Model):
    __tablename__ = 'modulo'
    id_modulo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_modulo = db.Column(db.String(100), nullable=False)
    asignaciones = db.relationship('RolPermiso', backref='modulo_rel')

class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_rol = db.Column(db.String(100))
    descripcion = db.Column(db.String(255))
    estatus = db.Column(db.String(20), default='ACTIVO')
    
    usuarios = db.relationship('Usuario', back_populates='rol')
    permisos = db.relationship('Permisos', secondary='rol_permiso', back_populates='roles')

class Permisos(db.Model):
    __tablename__ = 'permisos'
    id_permisos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_permisos = db.Column(db.String(100))
    
    roles = db.relationship('Rol', secondary='rol_permiso', back_populates='permisos')

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(100), unique=True)
    contrasenia = db.Column(db.String(255))
    def check_password(self, password):
        return check_password_hash(self.contrasenia, password)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    ultimo_acceso = db.Column(db.DateTime)
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado = db.Column(db.Boolean, default=False)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol')) 

    persona = db.relationship('Persona', back_populates='usuarios')
    rol = db.relationship('Rol', back_populates='usuarios')
    clientes = db.relationship('Cliente', back_populates='usuario')
    empleados = db.relationship('Empleado', back_populates='usuario')
    sesiones = db.relationship('Sesion', back_populates='usuario')

    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, password):
        self.contrasenia = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasenia, password)

class Sesion(db.Model):
    __tablename__ = 'sesion'
    id_sesion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token_sesion = db.Column(db.String(255))
    fecha_inicio = db.Column(db.DateTime)
    fecha_expiracion = db.Column(db.DateTime)
    fecha_cierre = db.Column(db.DateTime)
    direccion_ip = db.Column(db.String(45))
    dispositivo = db.Column(db.String(150))
    estado = db.Column(db.Enum('ACTIVA', 'CERRADA', 'EXPIRADA'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

    usuario = db.relationship('Usuario', back_populates='sesiones')

    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))

class Puesto(db.Model):
    __tablename__ = 'puesto'
    id_puesto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_puesto = db.Column(db.String(100))

    empleados = db.relationship('Empleado', back_populates='puesto')

class Empleado(db.Model):
    __tablename__ = 'empleado'
    id_empleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_contratacion = db.Column(db.Date)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_puesto = db.Column(db.Integer, db.ForeignKey('puesto.id_puesto'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

    persona = db.relationship('Persona', back_populates='empleados')
    puesto = db.relationship('Puesto', back_populates='empleados')
    usuario = db.relationship('Usuario', back_populates='empleados')
    citas = db.relationship('Cita', back_populates='empleado')
    horarios = db.relationship('Horario', secondary='empleado_horario', back_populates='empleados')

class Horario(db.Model):
    __tablename__ = 'horario'
    id_horario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dia = db.Column(db.Enum('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO'))
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)

    empleados = db.relationship('Empleado', secondary='empleado_horario', back_populates='horarios')

    empleado_horario = db.Table('empleado_horario',
    db.Column('id_empleado', db.Integer, db.ForeignKey('empleado.id_empleado'), primary_key=True),
    db.Column('id_horario', db.Integer, db.ForeignKey('horario.id_horario'), primary_key=True)
)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

    persona = db.relationship('Persona', back_populates='clientes')
    usuario = db.relationship('Usuario', back_populates='clientes')
    citas = db.relationship('Cita', back_populates='cliente')

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(100))
    servicios = db.relationship('Servicio', back_populates='categoria')

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_servicio = db.Column(db.String(150))
    precio = db.Column(db.Numeric(10, 2))
    duracion_minutos = db.Column(db.Integer)
    foto = db.Column(db.String(255))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))

    categoria = db.relationship('Categoria', back_populates='servicios')
    detalles_cita = db.relationship('DetalleCita', back_populates='servicio')
    insumos = db.relationship('InsumoServicio', back_populates='servicio')

class Cita(db.Model):
    __tablename__ = 'cita'
    id_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime)
    estatus = db.Column(db.Enum('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA'), default='PENDIENTE')
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_empleado'))

    cliente = db.relationship('Cliente', back_populates='citas')
    empleado = db.relationship('Empleado', back_populates='citas')
    detalles = db.relationship('DetalleCita', back_populates='cita')
    pagos = db.relationship('Pago', back_populates='cita')

class DetalleCita(db.Model):
    __tablename__ = 'detalle_cita'
    id_detalle_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cita = db.Column(db.Integer, db.ForeignKey('cita.id_cita'))
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'))
    subtotal = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2), default=0.00)

    cita = db.relationship('Cita', back_populates='detalles')
    servicio = db.relationship('Servicio', back_populates='detalles_cita')

class MetodoPago(db.Model):
    __tablename__ = 'metodo_pago'
    id_metodo_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_metodo = db.Column(db.String(100))

    pagos = db.relationship('Pago', back_populates='metodo_pago')
    detalles_pago = db.relationship('DetallePago', back_populates='metodo_pago')

class Promocion(db.Model):
    __tablename__ = 'promocion'
    id_promocion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255))
    tipo_promocion = db.Column(db.String(100))
    descripcion = db.Column(db.String(255))
    valor_descuento = db.Column(db.Numeric(10, 2))
    foto = db.Column(db.String(255))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')

    pagos = db.relationship('Pago', back_populates='promocion')

class Pago(db.Model):
    __tablename__ = 'pago'
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_pago = db.Column(db.DateTime)
    subtotal = db.Column(db.Numeric(10, 2))
    impuesto = db.Column(db.Numeric(10, 2))
    propina = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    id_cita = db.Column(db.Integer, db.ForeignKey('cita.id_cita'))
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('metodo_pago.id_metodo_pago'))
    id_promocion = db.Column(db.Integer, db.ForeignKey('promocion.id_promocion'))

    cita = db.relationship('Cita', back_populates='pagos')
    metodo_pago = db.relationship('MetodoPago', back_populates='pagos')
    promocion = db.relationship('Promocion', back_populates='pagos')
    detalles_pago = db.relationship('DetallePago', back_populates='pago')

class DetallePago(db.Model):
    __tablename__ = 'detalle_pago'
    id_detalle_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'))
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('metodo_pago.id_metodo_pago'))
    monto = db.Column(db.Numeric(10, 2))

    pago = db.relationship('Pago', back_populates='detalles_pago')
    metodo_pago = db.relationship('MetodoPago', back_populates='detalles_pago')


class Marca(db.Model):
    __tablename__ = 'marca'
    id_marca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_marca = db.Column(db.String(100))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    rfc = db.Column(db.String(13), db.ForeignKey('empresa.rfc'))

    empresa = db.relationship('Empresa', back_populates='marcas')
    productos = db.relationship('Producto', back_populates='marca')

class UnidadMedida(db.Model):
    __tablename__ = 'unidad_medida'
    id_unidad_medida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_unidad = db.Column(db.String(50))

    productos = db.relationship('Producto', back_populates='unidad_medida')

class Producto(db.Model):
    __tablename__ = 'producto'
    codigo_producto = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(150))
    stock_actual = db.Column(db.Numeric(10, 2))
    precio_compra = db.Column(db.Numeric(10, 2))
    precio_unitario = db.Column(db.Numeric(10, 2))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_marca = db.Column(db.Integer, db.ForeignKey('marca.id_marca'))
    id_unidad_medida = db.Column(db.Integer, db.ForeignKey('unidad_medida.id_unidad_medida'))

    marca = db.relationship('Marca', back_populates='productos')
    unidad_medida = db.relationship('UnidadMedida', back_populates='productos')
    insumos_servicio = db.relationship('InsumoServicio', back_populates='producto')
    inventario = db.relationship('InventarioProducto', back_populates='producto', uselist=False)
    movimientos = db.relationship('MovimientoInventario', back_populates='producto')
    detalles_compra = db.relationship('DetalleCompra', back_populates='producto')


class InsumoServicio(db.Model):
    __tablename__ = 'insumo_servicio'
    id_insumo_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'))
    codigo_producto = db.Column(db.String(50), db.ForeignKey('producto.codigo_producto'))
    cantidad_utilizada = db.Column(db.Numeric(10, 2))

    servicio = db.relationship('Servicio', back_populates='insumos')
    producto = db.relationship('Producto', back_populates='insumos_servicio')


class TipoProveedor(db.Model):
    __tablename__ = 'tipo_proveedor'
    id_tipo_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_proveedor = db.Column(db.String(100))
    proveedores = db.relationship('Proveedor', back_populates='tipo_proveedor')

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    rfc = db.Column(db.String(13), db.ForeignKey('empresa.rfc'))
    id_tipo_proveedor = db.Column(db.Integer, db.ForeignKey('tipo_proveedor.id_tipo_proveedor'))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')

    persona = db.relationship('Persona', back_populates='proveedores')
    empresa = db.relationship('Empresa', back_populates='proveedores')
    tipo_proveedor = db.relationship('TipoProveedor', back_populates='proveedores')
    compras = db.relationship('CompraProveedor', back_populates='proveedor')

class InventarioProducto(db.Model):
    __tablename__ = 'inventario_producto'
    codigo_producto = db.Column(db.String(50), db.ForeignKey('producto.codigo_producto'), primary_key=True)
    stock_minimo = db.Column(db.Integer, default=0)
    stock_maximo = db.Column(db.Integer, default=0)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', back_populates='inventario')

class MovimientoInventario(db.Model):
    __tablename__ = 'movimiento_inventario'
    id_movimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_producto = db.Column(db.String(50), db.ForeignKey('producto.codigo_producto'))
    tipo = db.Column(db.Enum('ENTRADA', 'SALIDA', 'AJUSTE'))
    cantidad = db.Column(db.Numeric(10, 2))
    motivo = db.Column(db.String(150))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', back_populates='movimientos')

class CompraProveedor(db.Model):
    __tablename__ = 'compra_proveedor'
    id_compra_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2))
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'))

    proveedor = db.relationship('Proveedor', back_populates='compras')
    detalles = db.relationship('DetalleCompra', back_populates='compra')

class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compra'
    id_detalle_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_compra_proveedor = db.Column(db.Integer, db.ForeignKey('compra_proveedor.id_compra_proveedor'))
    codigo_producto = db.Column(db.String(50), db.ForeignKey('producto.codigo_producto'))
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))

    compra = db.relationship('CompraProveedor', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalles_compra')

class HistorialEstatus(db.Model):
    __tablename__ = 'historial_estatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tabla_afectada = db.Column(db.String(100), nullable=False)
    id_registro = db.Column(db.Integer, nullable=False)
    estatus_anterior = db.Column(db.String(50))
    estatus_nuevo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    id_bitacora = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accion = db.Column(db.String(100))
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
    tabla_afectada = db.Column(db.String(100))
    id_registro_afectado = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))