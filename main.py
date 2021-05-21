from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from server.CCDRDriver import CCDRDriver
from interference.clusters.ecm import ECM

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.models.equipment import stringify

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer

from pprint import pprint


# NOTE: Only for testing


def query(driver: CCDRDriver, v: str):
    print("Q:", v)
    db = driver.database

    results = driver.get_raw_query_rankings(v)

    pretty_results = {
        tag: (db.get_equipment_by_id(tag), score) for tag, score in results.items()
    }
    print("A:", end=None)
    pprint(pretty_results)


if __name__ == "__main__":
    t = Interface(
        processor=ECM(distance_threshold=5.),
        transformers={
            "query_type": TypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        },
        scoring_calculator=ScoringCalculator(),
    )

    driver = CCDRDriver(
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

    query(driver, "Piscina municipal de Estremoz")
    query(driver, "Escola Secundária Rainha Santa Isabel")
    query(driver, "Colegio da noite")
    query(driver, "Colégio da noite")
    query(driver, "Estadio da Luz")
