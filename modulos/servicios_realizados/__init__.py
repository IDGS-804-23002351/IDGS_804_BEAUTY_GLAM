from flask import Blueprint

servicios_realizados_bp = Blueprint(
    'servicios_realizados_bp',
    __name__,
    template_folder='../../templates'
)

from . import routes