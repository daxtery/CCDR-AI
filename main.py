from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingModel
from server.CCDRDriver import ToyDriver
from interference.clusters.ecm import ECM

from interference.transformers.transformer_pipeline import NumpyToInstancePipeline, IdentityPipeline, Instance
from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.transformers.user_query_transformer import UserQueryTransformer, TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer, StringuifyEquipmentTransformer

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

    driver = ToyDriver(t, ranker=RankingModel(), stringuifier_transformers={
        "query": UserQueryTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        "equipment": StringuifyEquipmentTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
    }, database=DatabaseAcessor(), config={})

    driver.init_processor()
    pprint(driver.get_query_results("Cultura"))
