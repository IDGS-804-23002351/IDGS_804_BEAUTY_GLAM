from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Persona(db.Model):
    __tablename__ = 'persona'
    id_persona = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_persona = db.Column(db.String(50))
    apellidos = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(150))
    direccion = db.Column(db.String(255))

class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_rol = db.Column(db.String(100))

class Permisos(db.Model):
    __tablename__ = 'permisos'
    id_permisos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_permisos = db.Column(db.String(100))

class RolPermisos(db.Model):
    __tablename__ = 'rol_permisos'
    id_rol_permisos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))
    id_permisos = db.Column(db.Integer, db.ForeignKey('permisos.id_permisos'))

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(100), unique=True)
    contrasenia = db.Column(db.String(255))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    ultimo_acceso = db.Column(db.DateTime)
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado = db.Column(db.Boolean, default=False)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Puesto(db.Model):
    __tablename__ = 'puesto'
    id_puesto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_puesto = db.Column(db.String(100))

class Empleado(db.Model):
    __tablename__ = 'empleado'
    id_empleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_contratacion = db.Column(db.Date)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    id_puesto = db.Column(db.Integer, db.ForeignKey('puesto.id_puesto'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(100))

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_servicio = db.Column(db.String(150))
    precio = db.Column(db.Numeric(10, 2))
    duracion_minutos = db.Column(db.Integer)
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))

class Cita(db.Model):
    __tablename__ = 'cita'
    id_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime)
    estatus = db.Column(db.Enum('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA'), default='PENDIENTE')
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_empleado'))

class DetalleCita(db.Model):
    __tablename__ = 'detalle_cita'
    id_detalle_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cita = db.Column(db.Integer, db.ForeignKey('cita.id_cita'))
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'))
    subtotal = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2), default=0.0)

class MetodoPago(db.Model):
    __tablename__ = 'metodo_pago'
    id_metodo_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_metodo = db.Column(db.String(100))

class Promocion(db.Model):
    __tablename__ = 'promocion'
    id_promocion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255))
    tipo_promocion = db.Column(db.String(100))
    descripcion = db.Column(db.String(255))
    valor_descuento = db.Column(db.Numeric(10, 2))
    foto = db.Column(db.String(255))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')

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

class Empresa(db.Model):
    __tablename__ = 'empresa'
    rfc = db.Column(db.String(13), primary_key=True)
    nombre_empresa = db.Column(db.String(150))
    direccion = db.Column(db.String(255))
    contacto = db.Column(db.String(150))

class Marca(db.Model):
    __tablename__ = 'marca'
    id_marca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_marca = db.Column(db.String(100))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    rfc = db.Column(db.String(13), db.ForeignKey('empresa.rfc'))

class UnidadMedida(db.Model):
    __tablename__ = 'unidad_medida'
    id_unidad_medida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_unidad = db.Column(db.String(50))

class Producto(db.Model):
    __tablename__ = 'producto'
    codigo_producto = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(150))
    stock_actual = db.Column(db.Integer)
    precio_compra = db.Column(db.Numeric(10, 2))
    precio_unitario = db.Column(db.Numeric(10, 2))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    id_marca = db.Column(db.Integer, db.ForeignKey('marca.id_marca'))
    id_unidad_medida = db.Column(db.Integer, db.ForeignKey('unidad_medida.id_unidad_medida'))

class InsumoServicio(db.Model):
    __tablename__ = 'insumo_servicio'
    id_insumo_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'))
    codigo_producto = db.Column(db.String(50), db.ForeignKey('producto.codigo_producto'))
    cantidad_utilizada = db.Column(db.Numeric(10, 2))

class TipoProveedor(db.Model):
    __tablename__ = 'tipo_proveedor'
    id_tipo_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_proveedor = db.Column(db.String(100))

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona'))
    rfc = db.Column(db.String(13), db.ForeignKey('empresa.rfc'))
    id_tipo_proveedor = db.Column(db.Integer, db.ForeignKey('tipo_proveedor.id_tipo_proveedor'))
    estatus = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')

class CompraProveedor(db.Model):
    __tablename__ = 'compra_proveedor'
    id_compra_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_compra = db.Column(db.DateTime, default=datetime.datetime.now)
    total = db.Column(db.Numeric(10, 2))
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'))

class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    id_bitacora = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accion = db.Column(db.String(100))
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.now)
    tabla_afectada = db.Column(db.String(100))
    id_registro_afectado = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))