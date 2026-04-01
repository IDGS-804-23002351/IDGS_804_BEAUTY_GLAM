from flask import Blueprint

acceso_bp = Blueprint('acceso', __name__)

from . import routes