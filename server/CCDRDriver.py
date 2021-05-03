
from ccdr.transformers.equipment_transformer import StringuifyEquipmentTransformer
from ccdr.models.equipment import Equipment, stringify
from ccdr.ranking_model.ranking import RankingModel
from ccdr.models.user_query import UserQuery
from ccdr.ccdr_interface import ToyTypeInterface, TransformersDict
from server.InMemoryDatabase import get_equipment_by_id, get_all_equipments

from typing import Any, Dict, Iterator, List, Sequence, Tuple, cast

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy

import logging

logger = logging.getLogger('trigger_driver')
logger.setLevel(logging.INFO)


class ToyDriver:

    def __init__(
        self,
        interface: ToyTypeInterface,
        stringuifier_transformers: TransformersDict,
        ranker: RankingModel,
        config: Dict[str, Any]
    ):
        self.interface = interface
        self.ranker = ranker
        self.config = config
        self.stringuify_transformer = stringuifier_transformers
        self.stringuified_equipment_embeddings: Dict[str, numpy.ndarray] = {}

    def init_processor(self) -> "ToyDriver":
        logger.info("Initializing processor")

        for _id, equipment in get_all_equipments():
            instance = self.interface.try_create_instance_from_value(
                "equipment", equipment)

            assert instance
            self.interface.add(_id, instance)

            embedding = self.stringuify_transformer["equipment"].calculate_embedding(
                equipment)

            self.stringuified_equipment_embeddings[_id] = embedding

        return self

    def add_equipment_by_id(self, _id: str):
        equipment = get_equipment_by_id(_id)

        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.add(_id, instance)

        embedding = self.stringuify_transformer["equipment"].calculate_embedding(
            equipment)

        self.stringuified_equipment_embeddings[_id] = embedding

    def get_query_results(self, query: str):
        query_ = UserQuery(query)

        instance = self.interface.try_create_instance_from_value(
            "query", query_)

        assert instance

        relevant_equipments = self.interface.get_scorings_for(instance)

        stringify_embedding = self.stringuify_transformer["query"].calculate_embedding(
            query_)

        rankings: Dict[str, float] = {}

        for scoring in relevant_equipments:
            assert scoring.scored_tag

            embedding = self.stringuified_equipment_embeddings[scoring.scored_tag]

            ranking = self.ranker(stringify_embedding, embedding)
            rankings[scoring.scored_tag] = ranking

        # TODO: save for later?

        return [
            tag
            for tag, _ in sorted(rankings.items(), key=lambda s: s[1], reverse=True)
        ]
