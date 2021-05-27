from typing import Any, Iterator, List, Sequence, Tuple, Dict, cast
from typing_extensions import Protocol
from typing_extensions import TypedDict
from ccdr.models.equipment import Equipment, EquipmentArea, SocialEquipment, SportEquipment, HealthEquipment, CulturalEquipment, EducationEquipment, HospitalHealthEquipment, Escola
from pymongo import database, MongoClient
from bson.objectid import ObjectId

from dataclasses import asdict


class DatabaseAccessor(Protocol):

    def get_equipment_by_id(self, _id: str) -> Equipment:
        ...

    def get_all_equipments(self) -> Iterator[Tuple[str, Equipment]]:
        ...

    def get_feedback(self) -> Dict[str, List[Tuple[str, bool]]]:
        ...


class InMemoryDatabaseAccessor:

    toy_equipments: Dict[str, Equipment] = {
        "609964dc33c8033e28f0c1f9": SportEquipment(
            type_="Estádio",
            extras={"nome": "Estádio da Luz"},
            iluminado=True,
            tipo_piso="terra batida",
            mobilidade_reduzida_pratica=True,
            mobilidade_reduzida_assistencia=True,
        ),
        "609964dc33c8033e28f0c1fa": HospitalHealthEquipment(
            extras={"nome": "Centro de Saúde de Estremoz"},
            agrupamento_saude="Centro de Saúde Estremoz",
            centro_hospitalar="Hospital do Espírito Santo de Évora",
            valencias=["Radiologia"],
            especialidades=[],
        ),
        "609964dc33c8033e28f0c1fb": EducationEquipment(
            type_="Universidade",
            extras={"nome": "Universidade de Évora"},
            escolas=[Escola("Universidade")],
        ),
        "609964dc33c8033e28f0c1fc": EducationEquipment(
            type_="Escola",
            escolas=[Escola("Secundário"), Escola("Básico")],
            extras={"nome": "Agrupamento de Escolas Gabriel Pereira"},
        ),
        "609964dc33c8033e28f0c1fd": SocialEquipment(
            type_="Centro de dia",
            extras={"nome": "Centro Social Nossa Senhora Auxiliadora"},
            fins_lucrativos=True,
        ),
        "609964dc33c8033e28f0c1fe": CulturalEquipment(
            type_="Templo",
            acesso_gratuito=True,
            mobilidade_reduzida=True,
            extras={"nome": "Templo Romano Évora"},
        ),
    }

    def get_equipment_by_id(self, _id: str):
        return InMemoryDatabaseAccessor.toy_equipments[_id]

    def get_all_equipments(self):
        return InMemoryDatabaseAccessor.toy_equipments.items()

    def get_feedback(self):
        return {}


class BaseEquipmentDataFromDB(TypedDict):
    area: EquipmentArea
    type: str
    extras: Dict[str, str]


class FeedbackDataFromDB(TypedDict):
    equipment_id: str
    clicked: bool


class QueryFeedbackDataFromDB(TypedDict):
    query: str
    feedbacks: List[FeedbackDataFromDB]


class MongoDatabaseConfig(TypedDict):
    database_host: str
    database: str


class EquipmentMongoDatabaseAccessor:

    NAME = "equipment"

    @staticmethod
    def get_equipment_data_by_id(_id: str, database: database.Database) -> BaseEquipmentDataFromDB:
        equipment_collection = database[EquipmentMongoDatabaseAccessor.NAME]

        equipment_from_db = equipment_collection.find_one(
            {"_id": ObjectId(_id)})

        # FIXME: Is this good?
        assert equipment_from_db

        return equipment_from_db

    @staticmethod
    def get_all_equipment_data(database: database.Database) -> Iterator[Tuple[str, BaseEquipmentDataFromDB]]:
        equipment_collection = database[EquipmentMongoDatabaseAccessor.NAME]

        equipments_from_db = equipment_collection.find({})

        for equipment in equipments_from_db:
            yield str(equipment["_id"]), equipment


class EquipmentMongoDataTransformer:

    @staticmethod
    def transfrom_equipment_data_from_db(data: BaseEquipmentDataFromDB) -> Equipment:
        area = data["area"]
        type_ = data["type"]
        extras = data["extras"]

        data_ = cast(Dict[str, Any], data)

        if area == "Social":
            return SocialEquipment(
                type_,
                extras,
                data_["fins lucrativos"]
            )

        if area == "Cultura":
            return CulturalEquipment(
                type_,
                extras,
                data_["acesso gratuito"],
                data_["mobilidade reduzida"]
            )

        if area == "Educação":
            schools = list(
                map(
                    lambda dto: Escola(dto["grau ensino"]),
                    data_["escolas"]
                )
            )

            return EducationEquipment(type_, extras, schools)

        if area == "Desporto":
            return SportEquipment(
                type_,
                extras,
                data_["iluminado"],
                data_["tipo piso"],
                data_["mobilidade reduzida prática"],
                data_["mobilidade reduzida assistência"],
            )

        if area == "Saúde":
            if type_ == "Saúde Hospitalar":
                return HospitalHealthEquipment(
                    extras,
                    data_["agrupamento saude"],
                    data_["centro hospitalar"],
                    data_["valências"],
                    data_["especialidades"],
                )

            else:
                return HealthEquipment(type_, extras)

        else:  # We don't know what this is
            return Equipment(area, type_, extras)


class FeedbackMongoDatabaseAccessor:

    NAME = "queryfeedbacks"

    @staticmethod
    def get_query_feedback_data_by_id(_id: str, database: database.Database) -> QueryFeedbackDataFromDB:
        collection = database[FeedbackMongoDatabaseAccessor.NAME]

        from_db = collection.find_one(
            {"_id": ObjectId(_id)})

        # FIXME: Is this good?
        assert from_db

        return from_db

    @staticmethod
    def get_all_query_feedback_data(database: database.Database) -> Iterator[Tuple[str, QueryFeedbackDataFromDB]]:
        collection = database[FeedbackMongoDatabaseAccessor.NAME]

        from_db = collection.find({})

        for item in from_db:
            yield str(item["_id"]), item


class FeedbackMongoDataTransformer:

    @staticmethod
    def transfrom_query_feedback_data_from_db(data: QueryFeedbackDataFromDB) -> Tuple[str, List[Tuple[str, bool]]]:
        feedbacks = list(
            map(
                lambda f: (f["equipment_id"], f["clicked"]),
                data["feedbacks"]
            )
        )

        return (data["query"], feedbacks)


class MongoDatabaseAccessor:

    def __init__(self, config: MongoDatabaseConfig) -> None:
        self.database = config["database"]
        self.database_host = config["database_host"]

    def get_equipment_by_id(self, _id: str):
        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipment_from_db = EquipmentMongoDatabaseAccessor.get_equipment_data_by_id(
                _id, db)

        return EquipmentMongoDataTransformer.transfrom_equipment_data_from_db(equipment_from_db)

    def get_all_equipments(self):
        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipments_from_db = EquipmentMongoDatabaseAccessor.get_all_equipment_data(
                db)

        for _id, data in equipments_from_db:
            yield _id, EquipmentMongoDataTransformer.transfrom_equipment_data_from_db(data)

    def get_feedback(self):
        with MongoClient(self.database_host) as client:
            db = client[self.database]
            from_db = FeedbackMongoDatabaseAccessor.get_all_query_feedback_data(
                db)

        all_feedback: Dict[str, List[Tuple[str, bool]]] = {}

        for _, data in from_db:
            query, feedback = FeedbackMongoDataTransformer.transfrom_query_feedback_data_from_db(
                data)
            all_feedback.setdefault(query, [])
            all_feedback[query] += feedback

        return all_feedback
