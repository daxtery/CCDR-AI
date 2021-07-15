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


def parse_localizacao(obj: Dict[str, float]):
    return Localizacao(obj["latitude"], obj["longitude"])


def parse_social(details_raw: Dict[str, Optional[Any]]):
    organizacao = details_raw["organizacao"]

    if organizacao != None:
        organizacao = Organizacao(nome=organizacao)

    return SocialDetails(
        fins_lucrativos=details_raw["fins_lucrativos"],
        capacidade=details_raw["capacidade"],
        numero_de_utentes=details_raw["num_utentes"],
        organizacao=organizacao,
    )


def parse_cultura(details_raw: Dict[str, Optional[Any]]):
    tutela = details_raw["tutela"]

    if tutela != None:
        tutela = Organizacao(nome=tutela)

    return CulturalDetails(
        acesso_gratuito=details_raw["acesso_gratuito"],
        mobilidade_reduzida=details_raw["mobilidade_reduzida"],
        numero_visitantes_medio=details_raw["num_visitantes_medio"],
        tutela=tutela,
    )


def parse_educacao(details_raw: Dict[str, Optional[Any]]):
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


def parse_desporto(details_raw: Dict[str, Optional[Any]]):
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


def parse_saude(details_raw: Dict[str, Optional[Any]]):
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
    description = data["description"]
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


def parse_ActivityConsumption(obj: Dict[str, Any]):
    return ActivityConsumption(obj["activity"], obj["numberOfConsumers"])


def parse_ElectricConsumption(obj: Dict[str, Any]):
    return ElectricConsumption(obj["activity"], obj["consumption"])


def parse_Access(obj: Dict[str, Any]):
    return Access(obj["type"], obj["numAccess"])


def parse_ClientNumber(obj: Dict[str, Any]):
    return ClientNumber(obj["type"], obj["num"])


def parse_Company(obj: Dict[str, Any]):
    numStations = {
        s: v
        for s, v in obj["numStations"]
    } if obj["numStations"] is not None else None

    numPosts = {
        s: v
        for s, v in obj["numPosts"]
    } if obj["numPosts"] is not None else None

    return Company(numStations=numStations, numPosts=numPosts)


def parse_energia(details_raw: Dict[str, Optional[Any]]):
    tipo_energia = details_raw["tipo_energia"]
    num_operadores = details_raw["num_operadores"]
    lojas_por_operador = details_raw["num_operadores"]
    agentes_por_operador = details_raw["num_operadores"]

    finner_details_raw = details_raw["energy_details"]
    if finner_details_raw is None:
        return

    if tipo_energia == "luz":

        num_consumo_elec_p_atividade = {
            parse_localizacao(loc_raw): parse_ActivityConsumption(obj)
            for loc_raw, obj in finner_details_raw["num_consumo_elec_p_atividade"]
        } if finner_details_raw["num_consumo_elec_p_atividade"] is not None else None

        consumo_elec_p_atividade = {
            parse_localizacao(loc_raw): parse_ElectricConsumption(obj)
            for loc_raw, obj in finner_details_raw["consumo_elec_p_atividade"]
        } if finner_details_raw["consumo_elec_p_atividade"] is not None else None

        return LightDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            agentes_por_operador=agentes_por_operador,
            num_consumo_elec_p_atividade=num_consumo_elec_p_atividade,
            consumo_elec_p_atividade=consumo_elec_p_atividade,
        )

    elif tipo_energia == "gas":

        num_consumo_gas = {
            parse_localizacao(loc_raw): num
            for loc_raw, num in finner_details_raw["num_consumo_gas"]
        } if finner_details_raw["num_consumo_gas"] is not None else None

        consumo_gas = {
            parse_localizacao(loc_raw): num
            for loc_raw, num in finner_details_raw["consumo_gas"]
        } if finner_details_raw["consumo_gas"] is not None else None

        pontos_acesso = {
            parse_localizacao(loc_raw): num
            for loc_raw, num in finner_details_raw["pontos_acesso"]
        } if finner_details_raw["pontos_acesso"] is not None else None

        return GasDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            agentes_por_operador=agentes_por_operador,

            num_consumo_gas=num_consumo_gas,
            consumo_gas=consumo_gas,
            pontos_acesso=pontos_acesso,
        )


def parse_comunicacao(details_raw: Dict[str, Optional[Any]]):

    num_operadores = details_raw["num_operadores"]
    tipo_comunicacao = details_raw["tipo_comunicacao"]

    lojas_por_operador = {
        s: obj
        for s, obj in details_raw["lojas_por_operador"]
    } if details_raw["lojas_por_operador"] is not None else None

    cobertura_por_operador = defaultdict(dict)

    if details_raw["cobertura_por_operador"] is not None:
        for loc_raw, obj in details_raw["cobertura_por_operador"]:
            for name, value in obj["region"]:
                cobertura_por_operador[parse_localizacao(loc_raw)][name] = value

    communication_details = details_raw["communication_details"]
    if communication_details is None:
        return

    if tipo_comunicacao == "telefone":

        num_postos = {
            parse_localizacao(loc_raw): obj
            for loc_raw, obj in communication_details["num_postos"]
        } if communication_details["num_postos"] is not None else None

        num_acessos = {
            parse_localizacao(loc_raw): parse_Access(obj)
            for loc_raw, obj in communication_details["num_acessos"]
        } if communication_details["num_acessos"] is not None else None

        num_acessos_p_100 = {
            parse_localizacao(loc_raw): obj
            for loc_raw, obj in communication_details["num_acessos_p_100"]
        } if communication_details["num_acessos_p_100"] is not None else None

        num_postos_publicos = {
            parse_localizacao(loc_raw): obj
            for loc_raw, obj in communication_details["num_postos_publicos"]
        } if communication_details["num_postos_publicos"] is not None else None

        num_clientes = {
            parse_localizacao(loc_raw): parse_ClientNumber(obj)
            for loc_raw, obj in communication_details["num_clientes"]
        } if communication_details["num_clientes"] is not None else None

        return TelephoneDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            cobertura_por_operador=cobertura_por_operador,

            num_postos=num_postos,
            num_acessos=num_acessos,
            num_acessos_p_100=num_acessos_p_100,
            num_postos_publicos=num_postos_publicos,
            num_clientes=num_clientes
        )

    elif tipo_comunicacao == "internet":
        num_clientes_banda_larga = {
            s: obj
            for s, obj in communication_details["num_clientes_banda_larga"]
        } if communication_details["num_clientes_banda_larga"] is not None else None

        num_acessos_banda_larga_100 = {
            s: obj
            for s, obj in communication_details["num_acessos_banda_larga_100"]
        } if communication_details["num_acessos_banda_larga_100"] is not None else None

        num_acessos_banda_larga = {
            parse_localizacao(loc_raw): parse_Access(obj)
            for loc_raw, obj in communication_details["num_acessos_banda_larga"]
        } if communication_details["num_acessos_banda_larga"] is not None else None

        return InternetDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            cobertura_por_operador=cobertura_por_operador,

            num_clientes_banda_larga=num_clientes_banda_larga,
            num_acessos_banda_larga_100=num_acessos_banda_larga_100,
            num_acessos_banda_larga=num_acessos_banda_larga,
        )

    elif tipo_comunicacao == "correio":

        _ = {
            parse_localizacao(loc_raw): parse_Company(obj)
            for loc_raw, obj in communication_details
        }

        return MailDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            cobertura_por_operador=cobertura_por_operador,

            _=_,
        )

    elif tipo_comunicacao == "televisao":
        num_subscricoes = {
            parse_localizacao(loc_raw): obj
            for loc_raw, obj in communication_details["num_subscricoes"]
        } if communication_details["num_subscricoes"] is not None else None

        num_clientes = {
            s: obj
            for s, obj in communication_details["num_clientes"]
        } if communication_details["num_clientes"] is not None else None

        return TVDetails(
            num_operadores=num_operadores,
            lojas_por_operador=lojas_por_operador,
            cobertura_por_operador=cobertura_por_operador,

            num_subscricoes=num_subscricoes,
            num_clientes=num_clientes,
        )


def parse_infrastructure(data: Dict[str, Any]):
    area: InfrastructureArea = data["area"]
    description = data["description"]
    name = data["name"]
    extras = data["extras"]

    details_raw: DefaultDict[str, Optional[Any]] = defaultdict(
        lambda: None, data["equipmentDetails"])

    if area == "energia":
        details_obj = parse_energia(details_raw)

    elif area == "comunicacao":
        details_obj = parse_comunicacao(details_raw)

    else:  # We don't know what this is
        details_obj = None

    return Equipment(
        group="infra",
        area=area,
        description=description,
        name=name,
        extras=extras,
        horario=None,
        numero_de_equipamentos=None,
        localizacao=None,
        details=details_obj,
    )


def parse_equipment_or_infrastructure(data: Dict[str, Any]) -> Optional[Equipment]:

    group: Group = data["group"] if "group" in data else "equipment"

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
