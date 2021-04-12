from ccdr.models.user_query import UserQuery
from typing import Dict
from ccdr.models.equipment import Equipment
from ccdr.transformers import user_query_transformer
from ccdr.scoring import ToyScoringCalculator
from interference.clusters.ecm import ECM

from ccdr.ccdr_interface import ToyInterface
from ccdr.transformers.user_query_transformer import UserQueryTransformer
from ccdr.transformers.equipment_transformer import EquipmentTransformer

from pprint import pprint

class Helper:
    def __init__(self, t: ToyInterface) -> None:
        self.t = t
        self.x = 0
        self.map: Dict[str, Equipment] = {}

    def add(self, equipment: Equipment):
        instance = self.t.try_create_instance_from_value(
            "equipment", equipment)
        assert instance

        self.x += 1

        self.map[str(self.x)] = equipment
        return self.t.add(str(self.x), instance)

    def query(self, query: str):
        instance = self.t.try_create_instance_from_value("query", UserQuery(query))
        assert instance

        scorings = self.t.get_scorings_for(instance)
        return [
            (self.map[scoring.scored_tag], scoring.score)  # type: ignore
            for scoring in sorted(scorings, key=lambda s: s.score, reverse=True)
        ]


if __name__ == "__main__":
    t = ToyInterface(
        processor=ECM(distance_threshold=5.),
        transformers={
            "query": UserQueryTransformer(modelname='neuralmind/bert-large-portuguese-cased'),
            "equipment": EquipmentTransformer(modelname='neuralmind/bert-large-portuguese-cased')
        },
        scoring_calculator=ToyScoringCalculator()
    )

    h = Helper(t)
    h.add(Equipment(area="Desporto"))
    h.add(Equipment(area="Saúde"))
    h.add(Equipment(area="Educação"))
    h.add(Equipment(area="Social"))
    h.add(Equipment(area="Cultura"))

    pprint(h.query("Cultura"))
