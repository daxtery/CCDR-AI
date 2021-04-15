from server.CCDRDriver import ToyDriver
from ccdr.scoring import ToyScoringCalculator
from interference.clusters.ecm import ECM

from ccdr.ccdr_interface import ToyInterface
from ccdr.transformers.user_query_transformer import UserQueryTransformer
from ccdr.transformers.equipment_transformer import EquipmentTransformer

from pprint import pprint


if __name__ == "__main__":
    t = ToyInterface(
        processor=ECM(distance_threshold=5.),
        transformers={
            "query": UserQueryTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTransformer(modelname='neuralmind/bert-large-portuguese-cased')
        },
        scoring_calculator=ToyScoringCalculator()
    )

    driver = ToyDriver(t, {})
    driver.init_processor()
    pprint(driver.get_query_results("Cultura"))
