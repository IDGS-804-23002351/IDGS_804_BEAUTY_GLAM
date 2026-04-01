from flask import Blueprint

bitacora_bp = Blueprint('bitacora', __name__)

from . import routes