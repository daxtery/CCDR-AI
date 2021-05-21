from typing import Any, Iterator, Sequence, Tuple
from typing_extensions import Protocol
from typing_extensions import TypedDict
from ccdr.models.equipment import Equipment
from pymongo import database, MongoClient
from bson.objectid import ObjectId


class DatabaseAccessor(Protocol):

    def get_equipment_by_id(self, _id: str) -> Equipment:
        ...

    def get_all_equipments(self) -> Iterator[Tuple[str, Equipment]]:
        ...


class InMemoryDatabaseAccessor:

    toy_equipments = {
        "609964dc33c8033e28f0c1f9": Equipment(area="Desporto", type_="Estádio"),
        "609964dc33c8033e28f0c1fa": Equipment(area="Saúde", type_="Centro Hospitalar"),
        "609964dc33c8033e28f0c1fb": Equipment(area="Educação", type_="Universidade"),
        "609964dc33c8033e28f0c1fc": Equipment(area="Educação", type_="Escola"),
        "609964dc33c8033e28f0c1fd": Equipment(area="Social", type_="Centro de dia"),
        "609964dc33c8033e28f0c1fe": Equipment(area="Cultura", type_="Teatro"),
    }

    def get_equipment_by_id(self, _id: str):
        return InMemoryDatabaseAccessor.toy_equipments[_id]

    def get_all_equipments(self):
        return InMemoryDatabaseAccessor.toy_equipments.items()


class EquipmentDataFromDB(TypedDict):
    area: str
    type: str


class MongoDatabaseConfig(TypedDict):
    database_host: str
    database: str


class MongoDatabaseAccessor:

    def __init__(self, config: MongoDatabaseConfig) -> None:
        self.database = config["database"]
        self.database_host = config["database_host"]

    def _transfrom_equipment_data_from_db(self, data: EquipmentDataFromDB) -> Equipment:
        area = data["area"]
        type_ = data["type"]

        return Equipment(area, type_)

    def get_equipment_by_id(self, _id: str):
        collection_name = "equipment"

        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipment_collection = db[collection_name]

            equipment_from_db = equipment_collection.find_one(
                {"_id": ObjectId(_id)})

            # FIXME: Is this good?
            assert equipment_from_db

        return self._transfrom_equipment_data_from_db(equipment_from_db)

    def get_all_equipments(self):
        collection_name = "equipment"

        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipment_collection = db[collection_name]

            equipments_from_db = equipment_collection.find({})

        for equipment in equipments_from_db:
            yield str(equipment["_id"]), self._transfrom_equipment_data_from_db(equipment)
