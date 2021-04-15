from ccdr.models.user_query import UserQuery
from ccdr.ccdr_interface import ToyInterface
from server.InMemoryDatabase import get_equipment_by_id, get_all_equipments

from typing import Any, Dict, List, Sequence, cast

import logging

logger = logging.getLogger('trigger_driver')
logger.setLevel(logging.INFO)


class ToyDriver:

    def __init__(
        self,
        interface: ToyInterface,
        config: Dict[str, Any]
    ):
        self.interface = interface
        self.config = config

    def init_processor(self) -> "ToyDriver":
        logger.info("Initializing processor")

        for _id, equipment in get_all_equipments():
            instance = self.interface.try_create_instance_from_value(
                "equipment", equipment)

            assert instance
            self.interface.add(_id, instance)

        return self

    def add_equipment_by_id(self, _id: str):
        equipment = get_equipment_by_id(_id)

        instance = self.interface.try_create_instance_from_value(
            "equipment", equipment)

        assert instance
        self.interface.add(_id, instance)

    def get_query_results(self, query: str):
        instance = self.interface.try_create_instance_from_value(
            "query", UserQuery(query))

        assert instance

        # TODO: Cache this so we can have feedback?

        scorings = self.interface.get_scorings_for(instance)
        return [
            (self.interface.get_instances_by_tag(scoring.scored_tag)[0].value, scoring.score)  # type: ignore
            for scoring in sorted(scorings, key=lambda s: s.score, reverse=True)
        ]
