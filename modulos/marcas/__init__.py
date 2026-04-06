from flask import Blueprint

marcas_bp = Blueprint('marcas_bp', __name__)

from . import routes