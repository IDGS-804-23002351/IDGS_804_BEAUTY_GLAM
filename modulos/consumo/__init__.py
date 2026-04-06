from flask import Blueprint

consumo_bp = Blueprint('consumo_bp', __name__)

from . import routes