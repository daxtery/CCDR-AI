from server.database import DatabaseAccessor, MongoDatabaseConfig, InMemoryDatabaseAccessor, MongoDatabaseAccessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from server.CCDRDriver import CCDRDriver
from interference.clusters.gturbo import GTurbo

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.models.equipment import stringify

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer

from pprint import pprint

import json

# NOTE: Only for testing


def query(driver: CCDRDriver, v: str):
    print("Q:", v)
    db = driver.database_accessor

    results = driver.get_query_rankings_with_score(v)

    pretty_results = {
        tag: (db.get_equipment_by_id(tag), score) for tag, score in results.items()
    }
    print("A:", end=None)
    pprint(pretty_results)


if __name__ == "__main__":
    t = Interface(
        processor=GTurbo(epsilon_b=0.001, epsilon_n=0, lam=200, beta=0.9995,
                         alpha=0.95, max_age=200, r0=0.5, dimensions=1024),
        transformers={
            "query_type": TypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTypeTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
        },
        scoring_calculator=ScoringCalculator(),
    )

    with open('config.json', 'r') as f:
        config: MongoDatabaseConfig = json.load(f)

    driver = CCDRDriver(
        t,
        ranking=RankingExtension(
            tokenizer_name="neuralmind/bert-base-portuguese-cased",
            model_name="neuralmind/bert-base-portuguese-cased",
            ranker_factory=lambda: RankingModel(),
        ),
        stringify_equipment_func=stringify,
        database_accessor=MongoDatabaseAccessor(config),
    )

    driver.init_processor()

    query(driver, "Piscina municipal de Estremoz")
    query(driver, "Escola Secundária Rainha Santa Isabel")
    query(driver, "Colegio da noite")
    query(driver, "Colégio da noite")
    query(driver, "Estadio da Luz")
