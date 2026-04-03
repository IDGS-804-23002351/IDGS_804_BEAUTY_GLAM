from flask import Blueprint

proveedor = Blueprint(
    'proveedor',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes