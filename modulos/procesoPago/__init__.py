from flask import Blueprint

proceso_pago = Blueprint(
    'proceso_pago', 
    __name__, 
    template_folder='templates'
)

from . import routes