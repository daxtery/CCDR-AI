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

    @abc.abstractstaticmethod
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

    def __exit__(self):
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


def parse_social(details_raw: Dict[str, Any]):
    organizacao = details_raw["organizacao"]

    if organizacao != None:
        organizacao = Organizacao(nome=organizacao)

    return SocialDetails(
        fins_lucrativos=details_raw["fins_lucrativos"],
        capacidade=details_raw["capacidade"],
        numero_de_utentes=details_raw["num_utentes"],
        organizacao=organizacao,
    )


def parse_cultura(details_raw: Dict[str, Any]):
    tutela = details_raw["tutela"]

    if tutela != None:
        tutela = Organizacao(nome=tutela)

    return CulturalDetails(
        acesso_gratuito=details_raw["acesso_gratuito"],
        mobilidade_reduzida=details_raw["mobilidade_reduzida"],
        numero_visitantes_medio=details_raw["num_visitantes_médio"],
        tutela=tutela,
    )


def parse_educacao(details_raw: Dict[str, Any]):
    escolas = details_raw["escolas"]

    if escolas is not None:

        escolas = list(
            map(
                lambda dto: Escola(
                    dto["grau_ensino"],
                    capacidade=dto["capacidade"],
                    numero_de_alunos=dto["num_alunos"]
                ),
                escolas
            )
        )

    return EducationDetails(escolas)


def parse_desporto(details_raw: Dict[str, Any]):
    instalacoes_apoio = details_raw["instalacao_apoio"]

    if instalacoes_apoio is not None:
        instalacoes_apoio = list(
            map(lambda u: InstalacaoApoio(nome=u), instalacoes_apoio)
        )

    return SportDetails(
        iluminado=details_raw["iluminado"],
        tipo_piso=details_raw["tipo_piso"],
        mobilidade_reduzida_pratica=details_raw[
            "mobilidade_reduzida_pratica"],
        mobilidade_reduzida_assistencia=details_raw[
            "mobilidade_reduzida_assistencia"],
        capacidade=details_raw["capacidade"],
        instalacoes_apoio=instalacoes_apoio,
    )


def parse_saude(details_raw: Dict[str, Any]):
    numero_utentes = details_raw["num_utentes"]

    type_ = details_raw["tipo_saude"]
    details_raw = defaultdict(lambda: None, details_raw["healh_details"])

    if type_ == "saude_hospitalar":
        unidades = details_raw["tipo_unidades"]

        if unidades is not None:
            unidades = list(map(lambda u: Unidade(nome=u), unidades))

        num_equipamentos_por_especialidade = details_raw["num_equipamentos_por_especialidade"]

        if num_equipamentos_por_especialidade is not None:
            num_equipamentos_por_especialidade = dict(
                num_equipamentos_por_especialidade
            )

        return HospitalHealthDetails(
            agrupamento_saude=details_raw["agrupamento saude"],
            centro_hospitalar=details_raw["centro hospitalar"],
            valencias=details_raw["valencias"],
            especialidades=details_raw["especialidades"],
            numero_de_utentes=numero_utentes,
            numero_de_equipamentos_por_especialidade=num_equipamentos_por_especialidade,
            unidades=unidades,
        )

    elif type_ == "saude_geral":
        return GeneralHealthDetails(
            numero_de_utentes=numero_utentes,
            capacidade=details_raw["capacidade"],
            numero_centros_saude=details_raw["num_centros_saude"],
        )

    return None


def parse_equipment(data: Dict[str, Any]):
    area: EquipmentArea = data["area"]
    description = data["type"]
    name = data["name"]
    extras = data["extras"]

    optional_data: DefaultDict[str, Optional[Any]
                               ] = defaultdict(lambda: None, data)

    horario = optional_data["horario"]
    localizacao = optional_data["localizacao"]
    numero_de_equipamentos = optional_data["numero de equipamentos"]

    details_raw: DefaultDict[str, Optional[Any]] = defaultdict(
        lambda: None, data["equipmentDetails"])

    if area == "social":
        details_obj = parse_social(details_raw)

    elif area == "cultura":
        details_obj = parse_cultura(details_raw)

    elif area == "educacao":
        details_obj = parse_educacao(details_raw)

    elif area == "desporto":
        details_obj = parse_desporto(details_raw)

    elif area == "saude":
        details_obj = parse_saude(details_raw)

    else:  # We don't know what this is
        details_obj = None

    return Equipment(
        group="equipment",
        area=area,
        description=description,
        name=name,
        extras=extras,
        horario=horario,
        numero_de_equipamentos=numero_de_equipamentos,
        localizacao=localizacao,
        details=details_obj,
    )


def parse_infrastructure(data: Dict[str, Any]):
    pass


def parse_equipment_or_infrastructure(data: Dict[str, Any]) -> Optional[Equipment]:

    group: Group = data["group"]

    if group == "equipment":
        return parse_equipment(data)
    elif group == "infra":
        return parse_infrastructure(data)


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

        return parse_equipment_or_infrastructure(equipment_from_db)

    def get_all_equipments(self):
        with MongoCollectionAccessorWrapper(self.config["database_host"], self.config["database"], EquipmentMongoCollectionAccessor) as access:
            equipments_from_db = access.get_all_equipment_data()

        for _id, data in equipments_from_db:
            yield _id, parse_equipment_or_infrastructure(data)

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
