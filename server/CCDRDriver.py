
from ccdr.models.equipment import Equipment
import re
from server.database import DatabaseAccessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from ccdr.models.user_query import UserQuery
from ccdr.ccdr_interface import TransformersDict

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple, cast

from interference.interface import Interface

from itertools import chain
import unicodedata

import logging

logger = logging.getLogger('ccdr_driver')
logger.setLevel(logging.INFO)


def remove_accents(word: str) -> str:
    # https://pt.stackoverflow.com/questions/349415/como-remover-acento-em-python/349421
    normalized = ''.join(ch for ch in unicodedata.normalize(
        'NFKD', word) if not unicodedata.combining(ch))

    return normalized


KEYWORDS_REGEXES = {
    "estádio": [],
    "escola": [],
    "universidade": ["colégio"],
    "teatro": [],
    "centro de dia": [],
    "centro hospitalar": []
}


def extract_type_with_regex(query: str) -> Optional[str]:

    query_lower = query.lower()

    for keyword, regexes in KEYWORDS_REGEXES.items():
        # Estádio -> Estadio
        no_accents = remove_accents(keyword)

        if query_lower.find(keyword) != -1:
            return keyword

        if query_lower.find(no_accents) != -1:
            return keyword

        for regex in regexes:
            if re.match(regex, query_lower) is not None:
                return keyword

            no_accents_regex = remove_accents(regex)
            if re.match(no_accents_regex, query_lower) is not None:
                return keyword
    
    return None


class CCDRDriver:

    def __init__(
        self,
        interface: Interface,
        stringify_equipment_func: Callable[[Equipment], str],
        ranking: RankingExtension,
        database_accessor: DatabaseAccessor,
    ):
        self.interface = interface
        self.ranking = ranking
        self.stringify_equipment_func = stringify_equipment_func
        self.database_accessor = database_accessor

    def init_processor(self):
        logger.info("Initializing processor")

        for tag, equipment in self.database_accessor.get_all_equipments():
            self._add_equipment_with_tag(equipment, tag)

        return self

    def _add_equipment_with_tag(self, equipment: Equipment, tag: str):
        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.add(tag, instance)

        stringuified = self.stringify_equipment_func(equipment)
        self.ranking.equipment_was_added(tag, stringuified)

    def add_equipment_by_tag(self, tag: str):
        equipment = self.database_accessor.get_equipment_by_id(tag)

        self._add_equipment_with_tag(equipment, tag)

    def get_query_rankings(self, query: str):
        rankings = self.get_query_rankings_with_score(query)
        return [tag for tag in rankings]

    def get_query_rankings_with_score(self, query: str):
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