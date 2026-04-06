from flask import Blueprint

servicios_bp = Blueprint('servicios_bp', __name__)

from . import routes