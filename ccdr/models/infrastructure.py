import abc
from typing import Any, Generic, List, Dict, TypeVar, Tuple
from typing_extensions import Literal, Final, TypedDict
from ccdr.models.equipment import Localizacao


class RequiredEnergyDetails(TypedDict):
    tipo_energia: str
    energy_details: Any


class OptionalEnergyDetails(TypedDict, total=False):
    num_operadores: int
    lojas_por_operador: List[Tuple[str, int]]
    agentes_por_operador: List[Tuple[str, int]]


class EnergyDetails(RequiredEnergyDetails, OptionalEnergyDetails):
    pass


class GasDetails(TypedDict, total=False):
    num_consumo_gas: List[Tuple[Localizacao, int]]
    consumo_gas: List[Tuple[Localizacao, int]]
    pontos_acesso: List[Tuple[Localizacao, int]]


class ActivityConsumption(TypedDict):
    activity: str
    numberOfConsumers: int


class ElectricConsumption(TypedDict):
    activity: str
    consumption: float


class LightDetails(TypedDict, total=False):
    num_consumo_elec_p_atividade: List[Tuple[Localizacao, ActivityConsumption]]
    consumo_elec_p_atividade: List[Tuple[Localizacao, ElectricConsumption]]


class OptionalCommunicationDetails(TypedDict, total=False):
    num_operadores: int
    lojas_por_operador: List[Tuple[str, int]]
    cobertura_por_operador: List[Tuple[Localizacao, Tuple[str, int]]]


class RequiredCommunicationDetails(TypedDict):
    tipo_comunicacao: str
    communication_details: Any


class CommunicationDetails(RequiredCommunicationDetails, OptionalCommunicationDetails):
    pass


class Access(TypedDict):
    type: str
    numAccess: int


class ClientNumber(TypedDict):
    type: str
    num: int


class TelephoneDetails(TypedDict, total=False):
    num_postos: List[Tuple[Localizacao, int]]
    num_acessos: List[Tuple[Localizacao, Access]]
    num_acessos_p_100: List[Tuple[Localizacao, int]]
    num_postos_publicos: List[Tuple[Localizacao, int]]
    num_clientes: List[Tuple[Localizacao, ClientNumber]]


class InternetDetails(TypedDict, total=False):
    num_clientes_banda_larga: List[Tuple[str, int]]
    num_acessos_banda_larga_100: List[Tuple[str, int]]
    num_acessos_banda_larga: List[Tuple[Localizacao, Access]]


class Company(TypedDict):
    numStations: List[Tuple[str, int]]
    numPosts: List[Tuple[str, int]]


MailDetails = List[Tuple[Localizacao, Company]]


class TVDetails(TypedDict, total=False):
    num_subscricoes: List[Tuple[Localizacao, int]]
    num_clientes: List[Tuple[str, int]]
