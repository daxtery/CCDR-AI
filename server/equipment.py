from flask import (
    Blueprint
)

from .extensions import driver

eq_bp = Blueprint('equipment', __name__, url_prefix='/equipment')


@eq_bp.route('/<tag>', methods=['POST'])
def add_equipment(tag: str):
    driver.add_equipment_by_tag(tag)
    return "Ok"
