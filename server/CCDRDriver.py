
from ccdr.models.equipment import Equipment
import re
from server.database import DatabaseAccessor
from ccdr.ranking_model.ranking import RankingExtension, RankingModel
from ccdr.models.user_query import UserQuery

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple, cast

from interference.interface import Interface

from itertools import chain

import logging

logger = logging.getLogger('ccdr_driver')
logger.setLevel(logging.INFO)


class CCDRDriver:

    def __init__(
        self,
        interface: Interface,
        ranking_stringify_equipment_func: Callable[[Equipment], str],
        ranking: RankingExtension,
        database_accessor: DatabaseAccessor,
    ):
        self.interface = interface
        self.ranking = ranking
        self.ranking_stringify_equipment_func = ranking_stringify_equipment_func
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

    def add_equipment_by_tag(self, tag: str):
        equipment = self.database_accessor.get_equipment_by_id(tag)

        self._add_equipment_with_tag(equipment, tag)

    def update_equipment_by_tag(self, tag: str):
        equipment = self.database_accessor.get_equipment_by_id(tag)

        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.update(tag, instance)

    def remove_equipment_by_tag(self, tag: str):
        self.interface.remove(tag)

    def get_query_rankings(self, query: str, limit: int):
        rankings, matches_score = self.get_query_rankings_with_score(query)
        sorted_rankings = list(sorted([(tag, matches_score[tag])
                                       for tag in rankings], key=lambda k: k[1], reverse=True))

        if limit == 0:
            return sorted_rankings

        return sorted_rankings[:limit]

    def get_query_rankings_with_score(self, query: str):
        instance = self.interface.try_create_instance_from_value(
            "query_type", query)

        assert instance

        matches = self.interface.get_scorings_for(instance)

        relevant_equipments_and_scores: Dict[str, float] = {
            scoring.scored_tag: scoring.score
            for scoring in matches
            if scoring.scored_tag is not None
        }

        rankings = self.ranking.rank(
            query, list(relevant_equipments_and_scores.keys()))

        return rankings, relevant_equipments_and_scores

    def learn_with_feedback(self):
        all_feedback = self.database_accessor.get_feedback()
        self.ranking.learn(all_feedback)
        # TODO: maybe delete feedbacks here
