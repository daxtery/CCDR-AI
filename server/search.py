from flask import (
    Blueprint,
)

import json

from .extensions import driver

s_bp = Blueprint('search', __name__, url_prefix='/search')


@s_bp.route('/<query>', methods=['GET'])
def search(query: str):
    rankings = driver.get_query_rankings(query)
    return json.dumps(rankings)
