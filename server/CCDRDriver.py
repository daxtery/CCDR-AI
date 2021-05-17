
from ccdr.models.equipment import Equipment
import re
from server.database import DatabaseAcessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from ccdr.models.user_query import UserQuery
from ccdr.ccdr_interface import TransformersDict

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple, cast

from interference.interface import Interface

from itertools import chain
from functools import reduce

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


class CCDRDriver:

    def __init__(
        self,
        interface: Interface,
        stringify_equipment_func: Callable[[Equipment], str],
        ranking: RankingExtension,
        database: DatabaseAcessor,
        config: Dict[str, Any],
    ):
        self.interface = interface
        self.ranking = ranking
        self.config = config
        self.stringify_equipment_func = stringify_equipment_func
        self.database = database

    def init_processor(self):
        logger.info("Initializing processor")

        for tag, equipment in self.database.get_all_equipments():
            instance = self.interface.try_create_instance_from_value(
                "equipment", equipment)

            assert instance
            self.interface.add(tag, instance)

            stringuified = self.stringify_equipment_func(equipment)
            self.ranking.equipment_was_added(tag, stringuified)

        return self

    def add_equipment_by_tag(self, tag: str):
        equipment = self.database.get_equipment_by_id(tag)

        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.add(tag, instance)

        stringuified = self.stringify_equipment_func(equipment)
        self.ranking.equipment_was_added(tag, stringuified)

    def get_query_results(self, query: str):
        rankings = self.get_query_rankings(query)
        return [tag for tag in rankings]

    def get_raw_query_rankings(self, query: str):
        query_ = UserQuery(query)

        _type = extract_type_with_regex(query_.query)

        if _type is not None:
            instance = self.interface.try_create_instance_from_value(
                "query_type", _type)

            assert instance

            relevant_equipments_tags: List[str] = list(
                scoring.scored_tag for scoring in self.interface.get_scorings_for(instance)
                if scoring.scored_tag is not None
            )

        else:
            cluster_ids = self.interface.processor.get_cluster_ids()
            tags_by_cluster = map(lambda _cid: self.interface.processor.get_tags_in_cluster(_cid),
                                  cluster_ids)

            relevant_equipments_tags = list(chain(*tags_by_cluster))

        rankings = self.ranking.rank(query, relevant_equipments_tags)
        return rankings
