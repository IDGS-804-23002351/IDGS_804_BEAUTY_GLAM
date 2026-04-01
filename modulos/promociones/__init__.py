from flask import Blueprint

promociones = Blueprint(
    'promociones',
    __name__,
    template_folder='templates'
)

from . import routes