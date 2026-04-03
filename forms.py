from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField,PasswordField, SelectField, FloatField, TextAreaField,DateField, DateTimeField
from wtforms import validators
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DecimalField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp

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

    # Agregamos esto al final de forms.py
class BeautyUserForm(FlaskForm):
    # Datos para la tabla PERSONA
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=2, max=50)
    ])
    apellidos = StringField('Apellidos', [
        validators.DataRequired(message='Los apellidos son requeridos')
    ])
    email = EmailField('Correo', [
        validators.DataRequired(),
        validators.Email()
    ])
    telefono = StringField('Teléfono', [
        validators.DataRequired()
    ])

    # Datos para la tabla USUARIO (Control de acceso)
    username = StringField('Nombre de Usuario', [
        validators.DataRequired(),
        validators.Length(min=4, max=20)
    ])
    password = PasswordField('Contraseña', [
        validators.DataRequired(),
        validators.Length(min=5)
    ])
    
    id_rol = SelectField('Asignar Rol', coerce=int)

    especialidad = StringField('Especialidad', [validators.Optional()])

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
    
    # Validación personalizada para teléfono
    def validate_telefono(self, field):
        import re
        if not re.match(r'^[0-9]{10}$', field.data):
            raise validators.ValidationError('El teléfono debe contener exactamente 10 dígitos numéricos')
    
    # Validación personalizada para nombre de usuario (sin espacios)
    def validate_nombre_usuario(self, field):
        import re
        if ' ' in field.data:
            raise validators.ValidationError('El nombre de usuario no puede contener espacios')
        if not re.match(r'^[a-zA-Z0-9_.-]+$', field.data):
            raise validators.ValidationError('El nombre de usuario solo puede contener letras, números, puntos, guiones bajos y guiones')
        
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
    
    fecha_hora = DateTimeField('fecha_hora', [
        validators.DataRequired(message='La fecha y hora son requeridas')
    ], format='%Y-%m-%d %H:%M:%S')
    
    estatus = SelectField('estatus', choices=[
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('FINALIZADA', 'Finalizada')
    ], default='PENDIENTE', validators=[
        validators.Optional()
    ])
    
    # Campo para servicios (se manejará dinámicamente en el frontend)
    servicios = StringField('servicios', [
        validators.DataRequired(message='Debe seleccionar al menos un servicio')
    ], description='JSON con los servicios seleccionados')
    
    # Validación personalizada para fecha
    def validate_fecha_hora(self, field):
        from datetime import datetime
        if field.data and field.data < datetime.now():
            raise validators.ValidationError('No se pueden agendar citas en fechas pasadas')
        
        # Validar horario laboral (9:00 a 20:00)
        if field.data:
            hora = field.data.time()
            if hora.hour < 9 or hora.hour > 20:
                raise validators.ValidationError('La cita debe estar dentro del horario laboral (9:00 a 20:00)')

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
    
    id_cliente = SelectField('cliente', choices=[('', 'Todos')], coerce=int, validators=[validators.Optional()])
    
    id_empleado = SelectField('empleado', choices=[('', 'Todos')], coerce=int, validators=[validators.Optional()])
    
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
    nombre = StringField('Nombre', validators=[DataRequired()])
    tipo_promocion = StringField('Tipo de Promoción', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired()])
    valor_descuento = DecimalField('Valor Descuento', validators=[DataRequired()])
    
    foto = FileField('Foto', validators=[
        DataRequired(message="Debes seleccionar una imagen"),
        FileAllowed(['jpg', 'png', 'jpeg'], '¡Solo se permiten imágenes (jpg, png)!')
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

    rfc_empresa = StringField('rfc_empresa', [
        validators.Optional(),
        validators.Length(min=12, max=13, message='RFC invalido')
    ])

    id_tipo_proveedor = SelectField('id_tipo_proveedor', choices=[], coerce=int, validators=[
        validators.DataRequired(message='Debe seleccionar un tipo de proveedor')
    ])

    estatus = SelectField('estatus', choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    ], default='ACTIVO')

    # CORREGIR ESTA VALIDACIÓN
    def validate_telefono(self, field):
        import re
        if not re.match(r'^[0-9]{10}$', field.data):
            raise validators.ValidationError('El telefono debe contener exactamente 10 digitos numericos')

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