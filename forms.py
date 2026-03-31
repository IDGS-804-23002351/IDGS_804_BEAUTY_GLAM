from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField
from wtforms import validators


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