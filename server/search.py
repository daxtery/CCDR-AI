from flask import (
    Blueprint, request
)

import json

from .extensions import driver

s_bp = Blueprint('search', __name__, url_prefix='/search')


@s_bp.route('/<query>', methods=['GET'])
def search(query: str):
    limit = request.args.get('limit', default=0, type=int)
    rankings = driver.get_query_rankings(query, limit)
    return json.dumps(rankings)
