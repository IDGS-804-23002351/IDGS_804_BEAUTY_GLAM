from flask import Blueprint

unidades_bp = Blueprint('unidades_bp', __name__)

from . import routes