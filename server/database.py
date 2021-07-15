from ccdr.models.infrastructure import Access, ClientNumber, Company, GasDetails, InfrastructureArea, InternetDetails, LightDetails, ActivityConsumption, ElectricConsumption, MailDetails, TVDetails, TelephoneDetails
from collections import defaultdict
from typing import Any, DefaultDict, Iterator, List, Tuple, Dict, TypeVar, Optional, Generic
from typing_extensions import Protocol, Type, TypedDict
from ccdr.models.equipment import Equipment, EquipmentArea, Group, InstalacaoApoio, Localizacao, Horario, Organizacao, SocialDetails, SportDetails, CulturalDetails, EducationDetails, HospitalHealthDetails, GeneralHealthDetails, Escola, Unidade
from pymongo import MongoClient, collection
from bson.objectid import ObjectId
import abc


class DatabaseAccessor(Protocol):

    def get_equipment_by_id(self, _id: str) -> Equipment:
        ...

    def get_all_equipments(self) -> Iterator[Tuple[str, Equipment]]:
        ...

    def get_feedback(self) -> Dict[str, List[Tuple[str, float]]]:
        ...

    def get_unique_ids(self) -> List[str]:
        ...


class FeedbackDataFromDB(TypedDict):
    equipment_id: str
    score: float


class QueryFeedbackDataFromDB(TypedDict):
    query: str
    feedbacks: List[FeedbackDataFromDB]


class MongoDatabaseConfig(TypedDict):
    database_host: str
    database: str


class MongoAcessor(abc.ABC):
    def __init__(self, collection: collection.Collection):
        self.collection = collection

    @staticmethod
    @abc.abstractmethod
    def name() -> str:
        ...


T = TypeVar('T', bound=MongoAcessor)


class MongoCollectionAccessorWrapper(Generic[T]):

    def __init__(self, database_host: str, database: str, type_: Type[T]) -> None:
        self.database_host = database_host
        self.database = database
        self.type_ = type_

    def __enter__(self) -> T:
        self.client = MongoClient(self.database_host)
        db = self.client[self.database]
        name = self.type_.name()
        return self.type_(collection=db[name])

    def __exit__(self, exc_type, exc_value, tb):
        pass


class EquipmentMongoCollectionAccessor(MongoAcessor):
    def get_equipment_ids(self) -> List[str]:
        return self.collection.distinct('_id')

    def get_equipment_data_by_id(self, _id: str) -> Dict[str, Any]:
        equipment_from_db = self.collection.find_one(
            {"_id": ObjectId(_id)})

        # FIXME: Is this good?
        assert equipment_from_db

        return equipment_from_db

    def get_all_equipment_data(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        equipments_from_db = self.collection.find({})

        for equipment in equipments_from_db:
            yield str(equipment["_id"]), equipment

    @staticmethod
    def name():
        return "equipment"


class FeedbackMongoCollectionAccessor(MongoAcessor):

    def get_query_feedback_data_by_id(self, _id: str) -> QueryFeedbackDataFromDB:
        from_db = self.collection.find_one({"_id": ObjectId(_id)})

        # FIXME: Is this good?
        assert from_db

        return from_db

    def get_all_query_feedback_data(self) -> Iterator[Tuple[str, QueryFeedbackDataFromDB]]:
        from_db = self.collection.find({})

        for item in from_db:
            yield str(item["_id"]), item

    @staticmethod
    def name():
        return "queryfeedbacks"


def parse_query_feedback(data: QueryFeedbackDataFromDB) -> Tuple[str, List[Tuple[str, float]]]:
    feedbacks = list(
        map(
            lambda f: (str(f["equipment_id"]), f["score"]),
            data["feedbacks"]
        )
    )

    return (data["query"], feedbacks)


class MongoDatabaseAccessor:

    def __init__(self, config: MongoDatabaseConfig) -> None:
        self.config = config

    def get_equipment_by_id(self, _id: str):
        with MongoCollectionAccessorWrapper(self.config["database_host"], self.config["database"], EquipmentMongoCollectionAccessor) as access:
            equipment_from_db = access.get_equipment_data_by_id(_id)

        return equipment_from_db

    def get_all_equipments(self):
        with MongoCollectionAccessorWrapper(self.config["database_host"], self.config["database"], EquipmentMongoCollectionAccessor) as access:
            equipments_from_db = access.get_all_equipment_data()

        for _id, data in equipments_from_db:
            yield _id, data

    def get_unique_ids(self):
        with MongoCollectionAccessorWrapper(self.config["database_host"], self.config["database"], EquipmentMongoCollectionAccessor) as access:
            from_db = access.get_equipment_ids()

            return [str(id_obj) for id_obj in from_db]

    def get_feedback(self):
        with MongoCollectionAccessorWrapper(self.config["database_host"], self.config["database"], FeedbackMongoCollectionAccessor) as access:
            from_db = access.get_all_query_feedback_data()

        all_feedback: Dict[str, Dict[str, float]] = {}

        for _, data in from_db:
            query, feedback = parse_query_feedback(data)
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
