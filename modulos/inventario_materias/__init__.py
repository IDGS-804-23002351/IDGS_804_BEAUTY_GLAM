from flask import Blueprint

materias_primas_bp = Blueprint('materias_primas_bp', __name__)

from . import routes