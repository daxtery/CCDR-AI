
import re
from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingModel
from ccdr.models.user_query import UserQuery
from ccdr.ccdr_interface import TransformersDict

from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, cast

from interference.interface import Interface

from itertools import chain
from functools import reduce

import numpy

import logging

logger = logging.getLogger('trigger_driver')
logger.setLevel(logging.INFO)


def extract_type_with_regex(query: str) -> Optional[str]:
    KEYWORDS_REGEXES = {
        "estadio": ["estádio"],
        "escola": [],
        "universidade": ["col[e|é]gio"],
        "teatro": [],
        "centro de dia": [],
        "centro hospitalar": []
    }

    query_lower = query.lower()

    for keyword, regexes in KEYWORDS_REGEXES.items():
        if query_lower.find(keyword) != -1:
            return keyword

        for regex in regexes:
            if re.match(regex, query_lower) is not None:
                return keyword


class ToyDriver:

    def __init__(
        self,
        interface: Interface,
        stringuifier_transformers: TransformersDict,
        ranker: RankingModel,
        database: DatabaseAcessor,
        config: Dict[str, Any],
    ):
        self.interface = interface
        self.ranker = ranker
        self.config = config
        self.stringuify_transformer = stringuifier_transformers
        self.stringuified_equipment_embeddings: Dict[str, numpy.ndarray] = {}
        self.database = database

    def init_processor(self) -> "ToyDriver":
        logger.info("Initializing processor")

        for _id, equipment in self.database.get_all_equipments():
            instance = self.interface.try_create_instance_from_value(
                "equipment", equipment)

            assert instance
            self.interface.add(_id, instance)

            embedding = self.stringuify_transformer["equipment"].calculate_embedding(
                equipment)

            self.stringuified_equipment_embeddings[_id] = embedding

        return self

    def add_equipment_by_id(self, _id: str):
        equipment = self.database.get_equipment_by_id(_id)

        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.add(_id, instance)

        embedding = self.stringuify_transformer["equipment"].calculate_embedding(
            equipment)

        self.stringuified_equipment_embeddings[_id] = embedding

    def get_query_results(self, query: str):
        query_ = UserQuery(query)

        _type = extract_type_with_regex(query_.query)

        if _type is not None:
            instance = self.interface.try_create_instance_from_value(
                "query_type", _type)

            assert instance

            relevant_equipments_tags = (
                scoring.scored_tag for scoring in self.interface.get_scorings_for(instance)
                if scoring.scored_tag is not None  # FIXME: It shouldn't be?!
            )

        else:
            cluster_ids = self.interface.processor.get_cluster_ids()
            all_tags = map(lambda _cid: self.interface.processor.get_tags_in_cluster(_cid),
                           cluster_ids,
                           )

            relevant_equipments_tags = chain(*all_tags)

        stringify_embedding = self.stringuify_transformer["query"].calculate_embedding(
            query_)

        rankings: Dict[str, float] = {}

        for tag in relevant_equipments_tags:
            embedding = self.stringuified_equipment_embeddings[tag]

            ranking = self.ranker(stringify_embedding, embedding)
            rankings[tag] = ranking

        return [
            tag
            for tag, _ in sorted(rankings.items(), key=lambda s: s[1], reverse=True)
        ]
