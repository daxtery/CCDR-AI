from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from server.CCDRDriver import ToyDriver
from interference.clusters.ecm import ECM

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.models.equipment import stringify

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer

import numpy
from pprint import pprint


if __name__ == "__main__":
    t = Interface(
        processor=ECM(distance_threshold=5.),
        transformers={
            "query_type": TypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        },
        scoring_calculator=ScoringCalculator(),
    )

    driver = ToyDriver(
        t,
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
    pprint(driver.get_query_results("Cultura"))
