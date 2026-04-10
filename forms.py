from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField,PasswordField, SelectField, FloatField, TextAreaField,DateField, DateTimeField, HiddenField, ValidationError
from wtforms import validators, StringField, PasswordField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, DecimalField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp, Email, Length, Regexp, Optional

class UserForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional(),
        validators.NumberRange(min=1, max=999999, message='valor no valido')
    ])

    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=20, message='requiere min=4 max=20')
    ])

    apellidos = StringField('apellidos', [
        validators.DataRequired(message='El apellido es requerido')
    ])

    email = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingrese un correo valido')
    ])

    telefono = StringField('telefono', [
        validators.DataRequired(message='El telefono es requerido'),
        validators.Length(min=7, max=15, message='telefono invalido')
    ])

    especialidad = StringField('especialidad', [
        validators.Optional(),
        validators.Length(min=3, max=50, message='especialidad invalida')
    ])


class CursoForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional()
    ])

    nombre = StringField('nombre', [
        validators.DataRequired()
    ])

    descripcion = StringField('descripcion', [
        validators.Optional()
    ])

    maestro_id = IntegerField('maestro_id', [
        validators.DataRequired()
    ])

    # Forms para usuarios 
class BeautyUserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Correo', validators=[DataRequired(), Email()])
    
    telefono = StringField('Teléfono', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos numéricos.")
    ])
    
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(),
        Regexp(r'^\S+$', message="El nombre de usuario no puede contener espacios.")
    ])
    
    password = PasswordField('Contraseña', validators=[
        Optional(), 
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', 
               message="La contraseña debe incluir al menos una letra y un número.")
    ])
    
    id_rol = SelectField('Rol', coerce=int)
    especialidad = StringField('Especialidad')
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])

    def validate_fecha_nacimiento(self, field):
        hoy = date.today()
        edad = hoy.year - field.data.year - ((hoy.month, hoy.day) < (field.data.month, field.data.day))
        if edad < 12:
            raise ValidationError('El usuario debe tener al menos 12 años de edad.')

class ClienteForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional(),
        validators.NumberRange(min=1, max=999999, message='ID no válido')
    ])
    
    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    
    apellidos = StringField('apellidos', [
        validators.DataRequired(message='Los apellidos son requeridos'),
        validators.Length(min=2, max=100, message='Los apellidos deben tener entre 2 y 100 caracteres')
    ])
    
    telefono = StringField('telefono', [
        validators.DataRequired(message='El teléfono es requerido'),
        validators.Length(min=10, max=10, message='El teléfono debe tener 10 dígitos')
    ])
    
    correo = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingrese un correo válido'),
        validators.Length(max=150, message='El correo es muy largo')
    ])
    
    direccion = StringField('direccion', [
        validators.Optional(),
        validators.Length(max=255, message='La dirección es muy larga')
    ])
    fecha_nacimiento = DateField('fecha_nacimiento', [
        validators.Optional()
    ], format='%Y-%m-%d')
    
    genero = SelectField('genero', choices=[
        ('', 'Seleccione...'),
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
        ('Otro', 'Otro'),
        ('Sin especificar', 'Sin especificar')
    ], validators=[validators.Optional()])
    
    nombre_usuario = StringField('nombre_usuario', [
        validators.Optional(),  
        validators.Length(min=4, max=100, message='El usuario debe tener entre 4 y 100 caracteres')
    ])
    
    contrasenia = PasswordField('contrasenia', [
        validators.Optional(), 
        validators.Length(min=6, max=255, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_contrasenia = PasswordField('confirmar_contrasenia', [
        validators.Optional(),  
        validators.EqualTo('contrasenia', message='Las contraseñas no coinciden')
    ])
    
    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO', validators=[
        validators.Optional()
    ])
    
    def validate_telefono(self, field):
        import re
        if not re.match(r'^[0-9]{10}$', field.data):
            raise validators.ValidationError('El teléfono debe contener exactamente 10 dígitos numéricos')
    
    def validate_nombre_usuario(self, field):
        import re
        if field.data:  
            if ' ' in field.data:
                raise validators.ValidationError('El nombre de usuario no puede contener espacios')
            if not re.match(r'^[a-zA-Z0-9_.-]+$', field.data):
                raise validators.ValidationError('El nombre de usuario solo puede contener letras, números, puntos, guiones bajos y guiones')
    
    def validate_contrasenia(self, field):
        if field.data and len(field.data) < 8:
            raise validators.ValidationError('La contraseña debe tener al menos 8 caracteres')
    def validate_fecha_nacimiento(self, field):
        from datetime import date
        if field.data:
            if field.data > date.today():
                raise validators.ValidationError('La fecha de nacimiento no puede ser futura')
            
            edad = date.today().year - field.data.year
            if edad < 15:
                raise validators.ValidationError('El cliente debe ser mayor de 15 años')
class EmpleadoForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional(),
        validators.NumberRange(min=1, max=999999, message='ID no válido')
    ])
    
    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    
    apellidos = StringField('apellidos', [
        validators.DataRequired(message='Los apellidos son requeridos'),
        validators.Length(min=2, max=100, message='Los apellidos deben tener entre 2 y 100 caracteres')
    ])
    
    telefono = StringField('telefono', [
        validators.DataRequired(message='El teléfono es requerido'),
        validators.Length(min=10, max=10, message='El teléfono debe tener 10 dígitos')
    ])
    
    correo = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingrese un correo válido'),
        validators.Length(max=150, message='El correo es muy largo')
    ])
    
    direccion = StringField('direccion', [
        validators.Optional(),
        validators.Length(max=255, message='La dirección es muy larga')
    ])
    fecha_nacimiento = DateField('fecha_nacimiento', [
        validators.Optional()
    ], format='%Y-%m-%d')
    
    genero = SelectField('genero', choices=[
        ('', 'Seleccione...'),
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
        ('Otro', 'Otro'),
        ('Sin especificar', 'Sin especificar')
    ], validators=[validators.Optional()])
    id_puesto = SelectField('puesto', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un puesto')
    ])
    
    fecha_contratacion = DateField('fecha_contratacion', [
        validators.DataRequired(message='La fecha de contratación es requerida'),
        validators.Optional()
    ], format='%Y-%m-%d')
    
    nombre_usuario = StringField('nombre_usuario', [
        validators.DataRequired(message='El nombre de usuario es requerido'),
        validators.Length(min=4, max=100, message='El usuario debe tener entre 4 y 100 caracteres')
    ])
    
    contrasenia = PasswordField('contrasenia', [
        validators.DataRequired(message='La contraseña es requerida'),
        validators.Length(min=6, max=255, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_contrasenia = PasswordField('confirmar_contrasenia', [
        validators.DataRequired(message='Debe confirmar la contraseña'),
        validators.EqualTo('contrasenia', message='Las contraseñas no coinciden')
    ])
    
    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO', validators=[
        validators.Optional()
    ])
    
    # Validaciones personalizadas
    def validate_telefono(self, field):
        import re
        if not re.match(r'^[0-9]{10}$', field.data):
            raise validators.ValidationError('El teléfono debe contener exactamente 10 dígitos numéricos')
    
    def validate_nombre_usuario(self, field):
        import re
        if ' ' in field.data:
            raise validators.ValidationError('El nombre de usuario no puede contener espacios')
        if not re.match(r'^[a-zA-Z0-9_.-]+$', field.data):
            raise validators.ValidationError('El nombre de usuario solo puede contener letras, números, puntos, guiones bajos y guiones')
    
    def validate_fecha_contratacion(self, field):
        from datetime import date
        if field.data and field.data > date.today():
            raise validators.ValidationError('La fecha de contratación no puede ser futura')
    def validate_fecha_nacimiento(self, field):
        from datetime import date
        if field.data:
            if field.data > date.today():
                raise validators.ValidationError('La fecha de nacimiento no puede ser futura')
            
            edad = date.today().year - field.data.year
            if edad < 18:
                raise validators.ValidationError('El empleado debe ser mayor de 18 años')   
class FiltroClienteForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], validators=[validators.Optional()])
    
    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])


class FiltroEmpleadoForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], validators=[validators.Optional()])
    
    id_puesto = SelectField('puesto', choices=[('', 'Todos')], coerce=int, validators=[validators.Optional()])
    
    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])
class CambioPasswordForm(FlaskForm):
    contrasenia_actual = PasswordField('contrasenia_actual', [
        validators.DataRequired(message='La contraseña actual es requerida')
    ])
    
    contrasenia_nueva = PasswordField('contrasenia_nueva', [
        validators.DataRequired(message='La nueva contraseña es requerida'),
        validators.Length(min=6, max=255, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_contrasenia = PasswordField('confirmar_contrasenia', [
        validators.DataRequired(message='Debe confirmar la contraseña'),
        validators.EqualTo('contrasenia_nueva', message='Las contraseñas no coinciden')
    ])

class PromocionForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="El nombre es requerido")])
    tipo_promocion = StringField('Tipo de Promoción', validators=[DataRequired(message="El tipo de promoción es requerido")])
    descripcion = StringField('Descripción', validators=[DataRequired(message="La descripción es requerida")])
    valor_descuento = IntegerField('Valor de Descuento (%)', validators=[
        DataRequired(message="El descuento es obligatorio"),
        NumberRange(min=10, max=50, message="El descuento debe estar entre 10 y 50")
    ])
    
    foto = FileField('Foto', validators=[DataRequired(message="La foto es requerida"),
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], '¡Solo se permiten imágenes!')
    ])

class ProveedorForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional(),
        validators.NumberRange(min=1, max=999999, message='valor no valido')
    ])

    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=2, max=50, message='requiere min=2 max=50')
    ])

    apellidos = StringField('apellidos', [
        validators.DataRequired(message='Los apellidos son requeridos')
    ])

    telefono = StringField('telefono', [
        validators.DataRequired(message='El telefono es requerido'),
        validators.Length(min=10, max=10, message='telefono debe tener 10 digitos')
    ])

    correo = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingrese un correo valido')
    ])

    direccion = StringField('direccion', [
        validators.Optional()
    ])
    
    # NUEVOS CAMPOS
    fecha_nacimiento = DateField('fecha_nacimiento', [
        validators.Optional()
    ], format='%Y-%m-%d')
    
    genero = SelectField('genero', choices=[
        ('', 'Seleccione...'),
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
        ('Otro', 'Otro'),
        ('Sin especificar', 'Sin especificar')
    ], validators=[validators.Optional()])

    rfc_empresa = StringField('rfc_empresa', [
        validators.Optional(),
        validators.Length(min=12, max=13, message='RFC invalido')
    ])

    id_tipo_proveedor = SelectField('id_tipo_proveedor', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un tipo de proveedor')
    ])
    
    # Campos de usuario
    nombre_usuario = StringField('nombre_usuario', [
        validators.DataRequired(message='El nombre de usuario es requerido'),
        validators.Length(min=4, max=100, message='El usuario debe tener entre 4 y 100 caracteres')
    ])
    
    contrasenia = PasswordField('contrasenia', [
        validators.DataRequired(message='La contraseña es requerida'),
        validators.Length(min=6, max=255, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_contrasenia = PasswordField('confirmar_contrasenia', [
        validators.DataRequired(message='Debe confirmar la contraseña'),
        validators.EqualTo('contrasenia', message='Las contraseñas no coinciden')
    ])

    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO')

    def validate_telefono(self, field):
        import re
        if not re.match(r'^[0-9]{10}$', field.data):
            raise validators.ValidationError('El telefono debe contener exactamente 10 digitos numericos')
    
    def validate_nombre_usuario(self, field):
        import re
        if field.data:
            if ' ' in field.data:
                raise validators.ValidationError('El nombre de usuario no puede contener espacios')
            if not re.match(r'^[a-zA-Z0-9_.-]+$', field.data):
                raise validators.ValidationError('El nombre de usuario solo puede contener letras, números, puntos, guiones bajos y guiones')
    
    def validate_fecha_nacimiento(self, field):
        from datetime import date
        if field.data:
            if field.data > date.today():
                raise validators.ValidationError('La fecha de nacimiento no puede ser futura')
            
            edad = date.today().year - field.data.year
            if edad < 18:
                raise validators.ValidationError('El proveedor debe ser mayor de 18 años')
            
class FiltroProveedorForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], validators=[validators.Optional()])
    
    id_tipo_proveedor = SelectField('id_tipo_proveedor', choices=[('', 'Todos')], coerce=int, validators=[validators.Optional()])
    
    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])
class CitaForm(FlaskForm):
    id = IntegerField('id', [
        validators.Optional(),
        validators.NumberRange(min=1, max=999999, message='ID no válido')
    ])

    id_cliente = SelectField('cliente', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un cliente')
    ])

    id_empleado = SelectField('empleado', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un empleado')
    ])

    id_servicio = SelectField('servicio / promoción', choices=[], coerce=str, validators=[
        validators.DataRequired(message='Debe seleccionar un servicio o promoción')
    ])

    fecha_hora = DateTimeField('fecha_hora', [
        validators.DataRequired(message='La fecha y hora son requeridas')
    ], format='%Y-%m-%dT%H:%M')

    estatus = SelectField('estatus', choices=[
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('FINALIZADA', 'Finalizada')
    ], default='PENDIENTE', validators=[
        validators.Optional()
    ])
    
   

class DetalleCitaForm(FlaskForm):
    id_servicio = SelectField('servicio', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un servicio')
    ])
    
    descuento = FloatField('descuento', [
        validators.Optional(),
        validators.NumberRange(min=0, max=10000, message='El descuento no puede ser negativo')
    ], default=0)
    
    cantidad = IntegerField('cantidad', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=1, max=10, message='Cantidad no válida')
    ], default=1)
class FiltroCitaForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('FINALIZADA', 'Finalizada')
    ], validators=[validators.Optional()])

    id_cliente = SelectField('cliente', choices=[(0, 'Todos')], coerce=int, validators=[validators.Optional()])

    id_empleado = SelectField('empleado', choices=[(0, 'Todos')], coerce=int, validators=[validators.Optional()])

    fecha_inicio = DateField('fecha_inicio', [
        validators.Optional()
    ], format='%Y-%m-%d')

    fecha_fin = DateField('fecha_fin', [
        validators.Optional()
    ], format='%Y-%m-%d')

    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])


class ServicioRealizadoForm(FlaskForm):
    id_cita = HiddenField('id_cita')
    id_detalle_cita = HiddenField('id_detalle_cita')

    id_cliente = SelectField('cliente', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un cliente')
    ])

    id_empleado = SelectField('empleado', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un empleado')
    ])

    id_servicio = SelectField('servicio', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un servicio')
    ])

    fecha_hora = DateTimeField('fecha_hora', [
        validators.DataRequired(message='La fecha y hora es requerida')
    ], format='%Y-%m-%dT%H:%M')

    descuento = DecimalField('descuento', [
        validators.Optional(),
        validators.NumberRange(min=0, max=10000, message='Descuento no válido')
    ], default=0)

    estatus = SelectField('estatus', choices=[
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada')
    ], default='FINALIZADA', validators=[
        validators.DataRequired(message='Seleccione un estatus')
    ])

    submit = SubmitField('Guardar')


class FiltroServicioRealizadoForm(FlaskForm):
    id_cliente = SelectField('cliente', choices=[(0, 'Todos')], coerce=int, validators=[
        validators.Optional()
    ])

    id_empleado = SelectField('empleado', choices=[(0, 'Todos')], coerce=int, validators=[
        validators.Optional()
    ])

    id_servicio = SelectField('servicio', choices=[(0, 'Todos')], coerce=int, validators=[
        validators.Optional()
    ])

    fecha_inicio = DateTimeField('fecha_inicio', format='%Y-%m-%dT%H:%M', validators=[
        validators.Optional()
    ])

    fecha_fin = DateTimeField('fecha_fin', format='%Y-%m-%dT%H:%M', validators=[
        validators.Optional()
    ])

class ServicioForm(FlaskForm):
    id = HiddenField('id')

    nombre_servicio = StringField('nombre_servicio', [
        validators.DataRequired(message='El nombre del servicio es requerido'),
        validators.Length(min=2, max=150, message='Nombre no válido')
    ])

    precio = DecimalField('precio', [
        validators.DataRequired(message='El precio es requerido'),
        validators.NumberRange(min=0, max=999999, message='Precio no válido')
    ])

    duracion_minutos = IntegerField('duracion_minutos', [
        validators.DataRequired(message='La duración es requerida'),
        validators.NumberRange(min=1, max=600, message='Duración no válida')
    ])

    id_categoria = SelectField('id_categoria', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar una categoría')
    ])

    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO', validators=[
        validators.DataRequired(message='Debe seleccionar un estatus')
    ])

    foto = FileField('foto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes')
    ])


class FiltroServicioForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], validators=[validators.Optional()])

    id_categoria = SelectField('id_categoria', choices=[(0, 'Todas')], coerce=int, validators=[
        validators.Optional()
    ])

    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])


class RecetaInsumoForm(FlaskForm):
    id = HiddenField('id')
    id_servicio = HiddenField('id_servicio')

    codigo_producto = SelectField('codigo_producto', choices=[], validators=[
        validators.DataRequired(message='Debe seleccionar una materia prima')
    ])

    cantidad_utilizada = DecimalField('cantidad_utilizada', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=0.01, max=9999, message='Cantidad no válida')
    ])

class ProductoForm(FlaskForm):
    codigo_producto = StringField('codigo_producto', [
        validators.DataRequired(message='El código es requerido'),
        validators.Length(min=1, max=50, message='Código no válido')
    ])

    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=2, max=150, message='Nombre no válido')
    ])

    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO', validators=[
        validators.DataRequired(message='Seleccione un estatus')
    ])

    id_marca = SelectField('id_marca', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Seleccione una marca')
    ])

    id_unidad_medida = SelectField('id_unidad_medida', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Seleccione una unidad')
    ])

    stock_minimo = IntegerField('stock_minimo', [
        validators.DataRequired(message='El stock mínimo es requerido'),
        validators.NumberRange(min=0, max=999999, message='Stock mínimo no válido')
    ])

    stock_maximo = IntegerField('stock_maximo', [
        validators.DataRequired(message='El stock máximo es requerido'),
        validators.NumberRange(min=0, max=999999, message='Stock máximo no válido')
    ])


class FiltroProductoForm(FlaskForm):
    estatus = SelectField('estatus', choices=[
        ('', 'Todos'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], validators=[validators.Optional()])

    id_marca = SelectField('id_marca', choices=[(0, 'Todas')], coerce=int, validators=[
        validators.Optional()
    ])

    id_unidad_medida = SelectField('id_unidad_medida', choices=[(0, 'Todas')], coerce=int, validators=[
        validators.Optional()
    ])

    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])


class MovimientoInventarioForm(FlaskForm):
    codigo_producto = HiddenField('codigo_producto')

    tipo = SelectField('tipo', choices=[
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste')
    ], validators=[
        validators.DataRequired(message='Seleccione el tipo de movimiento')
    ])

    cantidad = IntegerField('cantidad', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=1, max=999999, message='Cantidad no válida')
    ])

    precio_compra = DecimalField('precio_compra', [
        validators.Optional(),
        validators.NumberRange(min=0, max=999999, message='Precio no válido')
    ])

    motivo = StringField('motivo', [
        validators.DataRequired(message='El motivo es requerido'),
        validators.Length(min=3, max=150, message='Motivo no válido')
    ])

class MarcaForm(FlaskForm):
    id = HiddenField('id')

    nombre_marca = StringField('nombre_marca', [
        validators.DataRequired(message='El nombre de la marca es requerido'),
        validators.Length(min=2, max=100, message='Nombre no válido')
    ])

    rfc = StringField('rfc', [
        validators.DataRequired(message='El RFC de la empresa es requerido'),
        validators.Length(min=12, max=13, message='RFC no válido')
    ])

    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO', validators=[
        validators.DataRequired(message='Seleccione un estatus')
    ])


class UnidadMedidaForm(FlaskForm):
    id = HiddenField('id')

    nombre_unidad = StringField('nombre_unidad', [
        validators.DataRequired(message='El nombre de la unidad es requerido'),
        validators.Length(min=1, max=50, message='Unidad no válida')
    ])

class FiltroConsumoForm(FlaskForm):
    buscar = StringField('buscar', [
        validators.Optional(),
        validators.Length(max=100)
    ])

    tipo = SelectField('tipo', choices=[
        ('', 'Todos'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste')
    ], validators=[validators.Optional()])


class AjusteConsumoForm(FlaskForm):
    codigo_producto = HiddenField('codigo_producto')

    cantidad = DecimalField('cantidad', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=0.01, max=999999, message='Cantidad no válida')
    ])

    motivo = StringField('motivo', [
        validators.DataRequired(message='El motivo es requerido'),
        validators.Length(min=3, max=150, message='Motivo no válido')
    ])