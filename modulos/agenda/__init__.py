# modulos/agenda/__init__.py
from flask import Blueprint

agenda_bp = Blueprint(
    'citas',
    __name__,
    url_prefix='/vistaClientes/citas'
)

from . import routers