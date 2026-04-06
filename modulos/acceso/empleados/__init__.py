from flask import Blueprint

empleado = Blueprint(
    'empleado',
    __name__,
    template_folder='templates',
    static_folder='static')
from . import routes