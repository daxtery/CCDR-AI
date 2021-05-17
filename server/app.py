from flask import Flask

from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from server.CCDRDriver import CCDRDriver
from interference.clusters.ecm import ECM

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.models.equipment import stringify

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer

import json

interface = Interface(
    processor=ECM(distance_threshold=5.),
    transformers={
        "query_type": TypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
    },
    scoring_calculator=ScoringCalculator(),
)

driver = CCDRDriver(
    interface,
    ranking=RankingExtension(
        tokenizer_name="neuralmind/bert-base-portuguese-cased",
        model_name="neuralmind/bert-base-portuguese-cased",
        ranker=RankingModel()
    ),
    stringify_equipment_func=stringify,
    database=DatabaseAcessor(),
    config={},
)

driver.init_processor()

app = Flask(__name__)


@app.route('/equipment/<tag>', methods=['POST'])
def add_equipment(tag: str):
    driver.add_equipment_by_tag(tag)
    return "Ok"


@app.route('/search/<query>', methods=['GET'])
def get_equipment(query: str):
    results = driver.get_query_results(query)
    response = json.dumps(results)
    return response


@app.route('/feedback/<query_hash>/<tag>', methods=['POST'])
def give_feedback(query_hash: str, tag: str):
    driver.give_feedback(query_hash, tag)
    return "Ok"
