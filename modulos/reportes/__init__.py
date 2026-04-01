from flask import Blueprint

reporte = Blueprint(
    'reporte', 
    __name__, 
    template_folder='templates'
)

from . import routes