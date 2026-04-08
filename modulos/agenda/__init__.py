# modulos/agenda/__init__.py
from flask import Blueprint

# Cambia el nombre del blueprint para evitar confusiones
agenda_bp = Blueprint(
    'agenda',  # Cambiado de 'citas' a 'agenda'
    __name__,
    url_prefix='/vistaClientes/citas'
)

from . import routers  # Asegúrate de que el archivo se llame routers.py o routes.py