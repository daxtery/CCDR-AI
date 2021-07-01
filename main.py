from server.database import DatabaseAccessor, MongoDatabaseConfig, MongoDatabaseAccessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel, EquipmentRankingModel
from server.CCDRDriver import CCDRDriver
from interference.clusters.ecm import ECM

from typing import List

from interference.interface import Interface
from interference.scoring import ScoringCalculator

from ccdr.transformers.user_query_transformer import TypeTransformer
from ccdr.transformers.equipment_transformer import EquipmentTypeTransformer, stringify

import json

import sys

# NOTE: Only for testing


def query(driver: CCDRDriver, v: str):
    print("Q:", v)

    db = driver.database_accessor

    results = driver.get_query_rankings_with_score(v)

    eqs = {
        tag: db.get_equipment_by_id(tag)
        for tag in results[0].keys()
    }

    pretty_results = {
        tag: {
            "data": str(eq) + str(eq.extras),
            "stringuified": stringify(eq),
            "rank score": str(results[0][tag]),
            "match score": str(results[1][tag])
        } for tag, eq in eqs.items()
    }

    print("A:", json.dumps(pretty_results,
          ensure_ascii=False, sort_keys=False, indent=4))


if __name__ == "__main__":
    t = Interface(
        processor=ECM(8.),
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

    database_accessor = MongoDatabaseAccessor(config)

    driver = CCDRDriver(
        t,
        ranking=RankingExtension(
            tokenizer_name="neuralmind/bert-base-portuguese-cased",
            model_name="neuralmind/bert-base-portuguese-cased",
            ranker_factory=ranker_factory,
            database_accessor = database_accessor,
        ),
        ranking_stringify_equipment_func=stringify,
        database_accessor=database_accessor,
    )

    driver.init_processor()

    original_stdout = sys.stdout

    with open('out.txt', 'w') as f:
        sys.stdout = f  # Change the standard output to the file we created.

        query(driver, "Templo Romano")
        query(driver, "Hospital Évora")
        query(driver, "Universidade de Evora")
        query(driver, "Evora Secundário")
        query(driver, "Estadio da Luz")

        sys.stdout = original_stdout  # Reset the standard output to its original value
