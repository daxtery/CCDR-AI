from ccdr.ranking_model.ranking import RankingModel
from ccdr.ccdr_interface import ToyTypeInterface
from server.CCDRDriver import ToyDriver
from interference.clusters.ecm import ECM

from interference.transformers.transformer_pipeline import NumpyToInstancePipeline, IdentityPipeline, Instance

from ccdr.transformers.user_query_transformer import UserQueryTransformer, UserQueryTypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer, StringuifyEquipmentTransformer

import numpy
from pprint import pprint


if __name__ == "__main__":
    t = ToyTypeInterface(
        processor=ECM(distance_threshold=5.),
        transformers={
            "query": UserQueryTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        },
    )

    driver = ToyDriver(t, ranker=RankingModel(), stringuifier_transformers={
        "query": UserQueryTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        "equipment": StringuifyEquipmentTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
    }, config={})

    driver.init_processor()
    pprint(driver.get_query_results("Cultura"))
