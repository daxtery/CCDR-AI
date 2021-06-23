from typing import Any, Iterator, List, Sequence, Tuple, Dict, cast
from typing_extensions import Protocol
from typing_extensions import TypedDict
from ccdr.models.equipment import Equipment, EquipmentArea, SocialEquipment, SportEquipment, HealthEquipment, CulturalEquipment, EducationEquipment, HospitalHealthEquipment, Escola
from pymongo import database, MongoClient
from bson.objectid import ObjectId


class DatabaseAccessor(Protocol):

    def get_equipment_by_id(self, _id: str) -> Equipment:
        ...

    def get_all_equipments(self) -> Iterator[Tuple[str, Equipment]]:
        ...

    def get_feedback(self) -> Dict[str, List[Tuple[str, float]]]:
        ...

    def get_unique_ids(self) -> List[str]:
        ...


class BaseEquipmentDataFromDB(TypedDict):
    name: str
    area: EquipmentArea
    type: str
    extras: Dict[str, str]
    equipmentDetails: Dict[str, Any]


class FeedbackDataFromDB(TypedDict):
    equipment_id: str
    score: float


class QueryFeedbackDataFromDB(TypedDict):
    query: str
    feedbacks: List[FeedbackDataFromDB]


class MongoDatabaseConfig(TypedDict):
    database_host: str
    database: str


class EquipmentMongoDatabaseAccessor:

    NAME = "equipment"

    @staticmethod
    def get_equipment_ids(database: database.Database) -> List[str]:

        equipment_collection = database[EquipmentMongoDatabaseAccessor.NAME]

        return equipment_collection.distinct('_id')

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
        name = data["name"]
        extras = data["extras"]

        data_ = cast(Dict[str, Any], data["equipmentDetails"])

        if area == "Social":
            return SocialEquipment(
                name=name,
                type_=type_,
                extras=extras,
                fins_lucrativos=data_["fins lucrativos"],
            )

        if area == "Cultura":
            return CulturalEquipment(
                name=name,
                type_=type_,
                extras=extras,
                acesso_gratuito=data_["acesso gratuito"],
                mobilidade_reduzida=data_["mobilidade reduzida"],
            )

        if area == "Educação":
            schools = list(
                map(
                    lambda dto: Escola(dto["grau ensino"]),
                    data_["escolas"]
                )
            )

            return EducationEquipment(name, type_, extras, schools)

        if area == "Desporto":
            return SportEquipment(
                name=name,
                type_=type_,
                extras=extras,
                iluminado=data_["iluminado"],
                tipo_piso=data_["tipo piso"],
                mobilidade_reduzida_pratica=data_[
                    "mobilidade reduzida prática"],
                mobilidade_reduzida_assistencia=data_[
                    "mobilidade reduzida assistência"],
            )

        if area == "Saúde":
            if type_ == "Saúde Hospitalar":
                return HospitalHealthEquipment(
                    name=name,
                    extras=extras,
                    agrupamento_saude=data_["agrupamento saude"],
                    centro_hospitalar=data_["centro hospitalar"],
                    valencias=data_["valências"],
                    especialidades=data_["especialidades"],
                )

            else:
                return HealthEquipment(
                    name=name,
                    type_=type_,
                    extras=extras,
                )

        else:  # We don't know what this is
            return Equipment(
                area=area,
                type_=type_,
                name=name,
                extras=extras
            )


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
    def transfrom_query_feedback_data_from_db(data: QueryFeedbackDataFromDB) -> Tuple[str, List[Tuple[str, float]]]:
        feedbacks = list(
            map(
                lambda f: (str(f["equipment_id"]), f["score"]),
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

    def get_unique_ids(self):

        with MongoClient(self.database_host) as client:

            db = client[self.database]
            from_db = EquipmentMongoDatabaseAccessor.get_equipment_ids(db)

            return [str(id_obj) for id_obj in from_db]

    def get_feedback(self):
        with MongoClient(self.database_host) as client:
            db = client[self.database]
            from_db = FeedbackMongoDatabaseAccessor.get_all_query_feedback_data(
                db)

        all_feedback: Dict[str, Dict[str, float]] = {}

        for _, data in from_db:
            query, feedback = FeedbackMongoDataTransformer.transfrom_query_feedback_data_from_db(
                data)
            all_feedback.setdefault(query, {})
            for tag, score in feedback:
                if tag in all_feedback[query]:
                    all_feedback[query][tag] = max(
                        all_feedback[query][tag], score)
                else:
                    all_feedback[query][tag] = score

        return {
            query: list(scores.items())
            for query, scores in all_feedback.items()
        }
