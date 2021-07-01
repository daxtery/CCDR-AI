"""Initialize any app extensions."""

from typing import List
from flask_apscheduler import APScheduler

from server.database import MongoDatabaseAccessor, MongoDatabaseConfig
from ccdr.ranking_model.ranking import EquipmentRankingModel, RankingExtension
from server.CCDRDriver import CCDRDriver
from interference.clusters.ecm import ECM

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer, stringify

import json

scheduler = APScheduler()

interface = Interface(
    processor=ECM(distance_threshold=5.),
    transformers={
        "query_type": TypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
    },
    scoring_calculator=ScoringCalculator(),
)

with open('config.json', 'r') as f:
    config: MongoDatabaseConfig = json.load(f)


def ranker_factory(unique_equipment_ids: List[str], training_epochs, learning_rate):

    return EquipmentRankingModel(unique_equipment_ids, training_epochs, learning_rate)

database_acessor = MongoDatabaseAccessor(config)

driver = CCDRDriver(
    interface,
    ranking=RankingExtension(
        database_accessor=database_acessor,
        tokenizer_name="neuralmind/bert-base-portuguese-cased",
        model_name="neuralmind/bert-base-portuguese-cased",
        ranker_factory=ranker_factory
    ),
    ranking_stringify_equipment_func=stringify,
    database_accessor=database_acessor,
)

driver.init_processor()

# ... any other stuff.. db, caching, sessions, etc.
