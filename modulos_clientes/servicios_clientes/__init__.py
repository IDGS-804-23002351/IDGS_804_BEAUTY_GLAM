from flask import Blueprint

cliente_servicios_bp = Blueprint(
    'cliente_servicios_bp',
    __name__,
    template_folder='templates'
)

from . import routes