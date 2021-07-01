from collections import defaultdict
from typing import Any, DefaultDict, Iterator, List, Mapping, Sequence, Tuple, Dict, TypeVar, cast, Optional
from typing_extensions import Protocol
from typing_extensions import TypedDict
from ccdr.models.equipment import Equipment, EquipmentArea, InstalacaoApoio, Localizacao, Horario, Organizacao, SocialDetails, SportDetails, CulturalDetails, EducationDetails, HospitalHealthDetails, GeneralHealthDetails, Escola, Unidade
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
    def get_equipment_data_by_id(_id: str, database: database.Database) -> Dict[str, Any]:
        equipment_collection = database[EquipmentMongoDatabaseAccessor.NAME]

        equipment_from_db = equipment_collection.find_one(
            {"_id": ObjectId(_id)})

        # FIXME: Is this good?
        assert equipment_from_db

        return equipment_from_db

    @staticmethod
    def get_all_equipment_data(database: database.Database) -> Iterator[Tuple[str, Dict[str, Any]]]:
        equipment_collection = database[EquipmentMongoDatabaseAccessor.NAME]

        equipments_from_db = equipment_collection.find({})

        for equipment in equipments_from_db:
            yield str(equipment["_id"]), equipment


T = TypeVar('T')


class EquipmentMongoDataTransformer:

    @staticmethod
    def transfrom_equipment_data_from_db(data: Dict[str, Any]) -> Equipment:

        area: EquipmentArea = data["area"]
        type_ = data["type"]
        name = data["name"]
        extras = data["extras"]

        optional_data: DefaultDict[str, Optional[Any]
                                   ] = defaultdict(lambda: None, data)

        horario = optional_data["horario"]
        localizacao = optional_data["localizacao"]
        numero_de_equipamentos = optional_data["numero de equipamentos"]

        details: DefaultDict[str, Optional[Any]] = defaultdict(
            lambda: None, data["equipmentDetails"])

        if area == "social":
            organizacao = details["organizacao"]

            if organizacao != None:
                organizacao = Organizacao(nome=organizacao)

            details_obj = SocialDetails(
                fins_lucrativos=details["fins_lucrativos"],
                capacidade=details["capacidade"],
                numero_de_utentes=details["num_utentes"],
                organizacao=organizacao,
            )

        elif area == "cultura":
            tutela = details["tutela"]

            if tutela != None:
                tutela = Organizacao(nome=tutela)

            details_obj = CulturalDetails(
                acesso_gratuito=details["acesso_gratuito"],
                mobilidade_reduzida=details["mobilidade_reduzida"],
                numero_visitantes_medio=details["num_visitantes_médio"],
                tutela=tutela,
            )

        elif area == "educacao":

            escolas = details["escolas"]

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

            details_obj = EducationDetails(escolas)

        elif area == "desporto":
            instalacoes_apoio = details["instalacao_apoio"]

            if instalacoes_apoio is not None:
                instalacoes_apoio = list(
                    map(lambda u: InstalacaoApoio(nome=u), instalacoes_apoio)
                )

            details_obj = SportDetails(
                iluminado=details["iluminado"],
                tipo_piso=details["tipo_piso"],
                mobilidade_reduzida_pratica=details[
                    "mobilidade_reduzida_pratica"],
                mobilidade_reduzida_assistencia=details[
                    "mobilidade_reduzida_assistencia"],
                capacidade=details["capacidade"],
                instalacoes_apoio=instalacoes_apoio,
            )

        elif area == "saude":
            numero_utentes = details["num_utentes"]

            type_ = details["tipo_saude"] or type_
            details = defaultdict(lambda: None, details["healh_details"])

            if type_ == "saude_hospitalar":
                unidades = details["tipo_unidades"]

                if unidades is not None:
                    unidades = list(map(lambda u: Unidade(nome=u), unidades))

                num_equipamentos_por_especialidade = details["num_equipamentos_por_especialidade"]

                if num_equipamentos_por_especialidade is not None:
                    num_equipamentos_por_especialidade = dict(
                        num_equipamentos_por_especialidade
                    )

                details_obj = HospitalHealthDetails(
                    agrupamento_saude=details["agrupamento saude"],
                    centro_hospitalar=details["centro hospitalar"],
                    valencias=details["valencias"],
                    especialidades=details["especialidades"],
                    numero_de_utentes=numero_utentes,
                    numero_de_equipamentos_por_especialidade=num_equipamentos_por_especialidade,
                    unidades=unidades,
                )

            elif type_ == "saude_geral":
                details_obj = GeneralHealthDetails(
                    numero_de_utentes=numero_utentes,
                    capacidade=details["capacidade"],
                    numero_centros_saude=details["num_centros_saude"],
                )

            else:  # We don't know what this is
                details_obj = None

        else:  # We don't know what this is
            details_obj = None

        return Equipment(
            area=area,
            type_=type_,
            name=name,
            extras=extras,
            horario=horario,
            numero_de_equipamentos=numero_de_equipamentos,
            localizacao=localizacao,
            details=details_obj,
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
