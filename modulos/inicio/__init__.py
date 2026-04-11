from flask import Blueprint

inicio_bp = Blueprint('inicio', __name__)

from . import routes